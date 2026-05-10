
#include <arpa/inet.h>
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <netdb.h>
#include <netinet/in.h>
#include <poll.h>
#include <signal.h>     // signal(SIGPIPE, SIG_IGN) 需要
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include "data.h"       // get/set/delete 的实现（资源数组操作）
#include "http.h"       // parse_request + request 结构体等
#include "util.h"       // string 类型、connection_state 等（skeleton 提供）

#define MAX_RESOURCES 100

/*
 * resources 是一个资源表：
 *   - skeleton 给了 tuple 结构（在 data.h 里）
 *   - 静态资源先预置 3 个
 *   - 动态资源后续会通过 set() 写入（例如 PUT /dynamic/hello）
 *
 * 注意：这里数组大小是 100，但一开始只初始化了 3 条，剩下默认是空的。
 */
struct tuple resources[MAX_RESOURCES] = {
    {"/static/foo", "Foo", sizeof("Foo") - 1},
    {"/static/bar", "Bar", sizeof("Bar") - 1},
    {"/static/baz", "Baz", sizeof("Baz") - 1},
};

/* =========================
 * DHT / Chord 相关定义
 * ========================= */

// DHT 消息类型
enum dht_flags {
    DHT_LOOKUP = 0,
    DHT_REPLY = 1,
    DHT_STABILIZE = 2,
    DHT_NOTIFY = 3,
    DHT_JOIN = 4
};

// DHT 消息格式 (11 bytes): flags(1) + hash(2) + id(2) + ip(4) + port(2)
#pragma pack(push, 1)
struct dht_message {
    uint8_t flags;
    uint16_t hash;
    uint16_t peer_id;
    uint8_t peer_ip[4];
    uint16_t peer_port;
};
#pragma pack(pop)

// Peer 信息结构
struct peer_info {
    uint16_t id;
    char ip[16];
    uint16_t port;
    int valid;
};

// 全局 DHT 状态
static struct {
    uint16_t self_id;
    char self_ip[16];
    uint16_t self_port;
    struct peer_info predecessor;
    struct peer_info successor;
    int udp_sock;
    
    // Lookup 缓存 (简单实现：缓存最近的一次 lookup 结果)
    uint16_t cached_hash;
    struct peer_info cached_responsible;
    int cache_valid;
} dht_state;

/* =========================
 * 哈希函数 (匹配 Python 测试的实现)
 * ========================= */
static uint16_t dht_hash(const char *data, size_t len) {
    uint32_t hash_val = 0;
    
    // 处理每两个字节
    for (size_t i = 0; i < len; i += 2) {
        uint16_t word;
        if (i + 1 < len) {
            word = ((uint8_t)data[i] << 8) | (uint8_t)data[i + 1];
        } else {
            // 奇数长度，最后一字节补0
            word = ((uint8_t)data[i] << 8) | 0;
        }
        hash_val += word;
    }
    
    // 折叠进位
    hash_val = (hash_val & 0xffff) + (hash_val >> 16);
    
    // 取反
    hash_val = ~hash_val & 0xffff;
    
    return (uint16_t)hash_val;
}

/* =========================
 * 判断 hash 是否在 (pred_id, self_id] 区间
 * 环形判断
 * ========================= */
static int is_responsible(uint16_t hash) {
    if (!dht_state.predecessor.valid) {
        return 1;  // 没有前驱，自己负责所有
    }
    
    uint16_t pred_id = dht_state.predecessor.id;
    uint16_t self_id = dht_state.self_id;
    
    if (pred_id < self_id) {
        // 正常情况：pred_id < hash <= self_id
        return (pred_id < hash && hash <= self_id);
    } else {
        // 跨越0点：hash > pred_id 或 hash <= self_id
        return (hash > pred_id || hash <= self_id);
    }
}

/* =========================
 * 判断 hash 是否在 (self_id, succ_id] 区间
 * ========================= */
static int successor_responsible(uint16_t hash) {
    if (!dht_state.successor.valid) {
        return 0;
    }
    
    uint16_t self_id = dht_state.self_id;
    uint16_t succ_id = dht_state.successor.id;
    
    if (self_id < succ_id) {
        // 正常情况：self_id < hash <= succ_id
        return (self_id < hash && hash <= succ_id);
    } else {
        // 跨越0点：hash > self_id 或 hash <= succ_id
        return (hash > self_id || hash <= succ_id);
    }
}

/* =========================
 * 发送 DHT 消息
 * ========================= */
static void send_dht_message(const char *dest_ip, uint16_t dest_port,
                             uint8_t flags, uint16_t hash,
                             uint16_t peer_id, const char *peer_ip, uint16_t peer_port) {
    struct dht_message msg;
    msg.flags = flags;
    msg.hash = htons(hash);
    msg.peer_id = htons(peer_id);
    msg.peer_port = htons(peer_port);
    
    // 转换 IP 地址
    struct in_addr addr;
    inet_pton(AF_INET, peer_ip, &addr);
    memcpy(msg.peer_ip, &addr.s_addr, 4);
    
    // 目标地址
    struct sockaddr_in dest;
    memset(&dest, 0, sizeof(dest));
    dest.sin_family = AF_INET;
    dest.sin_port = htons(dest_port);
    inet_pton(AF_INET, dest_ip, &dest.sin_addr);
    
    sendto(dht_state.udp_sock, &msg, sizeof(msg), 0,
           (struct sockaddr *)&dest, sizeof(dest));
    
    fprintf(stderr, "DHT: Sent message flags=%d hash=%d to %s:%d\n",
            flags, hash, dest_ip, dest_port);
}

/* =========================
 * 处理收到的 DHT 消息
 * ========================= */
static void handle_dht_message(void) {
    struct dht_message msg;
    struct sockaddr_in sender;
    socklen_t sender_len = sizeof(sender);
    
    ssize_t n = recvfrom(dht_state.udp_sock, &msg, sizeof(msg), 0,
                         (struct sockaddr *)&sender, &sender_len);
    
    if (n != sizeof(msg)) {
        fprintf(stderr, "DHT: Received invalid message size %zd\n", n);
        return;
    }
    
    uint8_t flags = msg.flags;
    uint16_t hash = ntohs(msg.hash);
    uint16_t peer_id = ntohs(msg.peer_id);
    uint16_t peer_port = ntohs(msg.peer_port);
    
    // 解析 peer IP
    struct in_addr peer_addr;
    memcpy(&peer_addr.s_addr, msg.peer_ip, 4);
    char peer_ip[16];
    inet_ntop(AF_INET, &peer_addr, peer_ip, sizeof(peer_ip));
    
    fprintf(stderr, "DHT: Received flags=%d hash=%d from peer %d @ %s:%d\n",
            flags, hash, peer_id, peer_ip, peer_port);
    
    switch (flags) {
        case DHT_LOOKUP:
            // 收到 lookup 请求
            // 检查我们的 successor 是否负责这个 hash
            if (successor_responsible(hash)) {
                // Successor 负责 -> 发送 reply 给原始请求者
                send_dht_message(peer_ip, peer_port,
                                DHT_REPLY, dht_state.self_id,
                                dht_state.successor.id,
                                dht_state.successor.ip,
                                dht_state.successor.port);
            } else {
                // 转发给 successor
                if (dht_state.successor.valid) {
                    send_dht_message(dht_state.successor.ip,
                                    dht_state.successor.port,
                                    DHT_LOOKUP, hash,
                                    peer_id, peer_ip, peer_port);
                }
            }
            break;
            
        case DHT_REPLY:
            // 收到 reply - 缓存结果
            fprintf(stderr, "DHT: Reply received - responsible peer is %d @ %s:%d\n",
                    peer_id, peer_ip, peer_port);
            dht_state.cached_hash = hash;
            dht_state.cached_responsible.id = peer_id;
            strncpy(dht_state.cached_responsible.ip, peer_ip, 15);
            dht_state.cached_responsible.ip[15] = '\0';
            dht_state.cached_responsible.port = peer_port;
            dht_state.cached_responsible.valid = 1;
            dht_state.cache_valid = 1;
            break;
            
        default:
            fprintf(stderr, "DHT: Unknown message type %d\n", flags);
            break;
    }
}

/* =========================
 * 一些 URI 判断函数
 * ========================= */

/*
 * 判断是不是 /static/ 开头
 * 例如：
 *   /static/foo -> true
 *   /static/abc -> true
 *   /dynamic/x -> false
 */
static int is_static_prefix(const char *uri) {
    return (strncmp(uri, "/static/", 8) == 0);
}

/*
 * 判断是不是 /dynamic/ 开头
 */
static int is_dynamic_prefix(const char *uri) {
    return (strncmp(uri, "/dynamic/", 9) == 0);
}

/*
 * 静态资源只允许精确的三条路径：
 *   /static/foo
 *   /static/bar
 *   /static/baz
 *
 * 例如：
 *   /static/foo -> true
 *   /static/foo123 -> false
 */
static int is_static_exact(const char *uri) {
    return (strcmp(uri, "/static/foo") == 0 ||
            strcmp(uri, "/static/bar") == 0 ||
            strcmp(uri, "/static/baz") == 0);
}

/*
 * 关键规则：只允许 /dynamic/<name> 这一层，不允许再有更多 '/'
 *
 * 合法：
 *   /dynamic/hello
 *   /dynamic/a
 *
 * 不合法：
 *   /dynamic/           （name 为空）
 *   /dynamic/hello/hi   （name 中包含 '/'）
 *
 * 这样做的目的：
 *   防止出现 "/dynamic/hello/hello" 这种路径被 data.c 的 delete/get 误匹配，
 *   造成把 /dynamic/hello 给删掉了。
 */
static int is_dynamic_valid(const char *uri) {
    // 必须先是 /dynamic/ 开头
    if (!is_dynamic_prefix(uri)) return 0;

    // name 指向 /dynamic/ 后面的部分
    const char *name = uri + 9;          // 跳过 "/dynamic/"
    if (*name == '\0') return 0;         // /dynamic/ 后面不能为空

    // name 里不允许再出现 '/'
    if (strchr(name, '/') != NULL) return 0;

    return 1;
}

/* =========================
 * 发送 HTTP 回复
 * ========================= */

/*
 * send_reply_to_client:
 *   根据 req->method 和 req->uri 决定返回什么 HTTP 响应
 *
 * 设计点：
 *   - 为了 skeleton 最稳：每次响应都加 Connection: close
 *   - 发送完后 shutdown + close，确保下一次 curl 可以重新连接（不会卡在"只允许一个连接"）
 */
static void send_reply_to_client(int conn, struct request *req) {
    char buffer[HTTP_MAX_SIZE];   // 复用一个大 buffer 组装响应
    char *reply = buffer;         // reply 指针可能指向 buffer，也可能指向常量字符串
    size_t reply_len = 0;

    // 打印调试信息：收到什么请求
    fprintf(stderr, "Handling %s request for %s (%lu byte payload)\n",
            req->method, req->uri, (unsigned long)req->payload_length);

    // 我们统一让连接关闭：每次请求一个连接（对测试更稳定）
    const char *conn_close_hdr = "Connection: close\r\n";

    /* ================= DHT 路由检查 ================= */
    // 对于非 /static/ 开头的 URI，需要检查 DHT 路由
    if (!is_static_prefix(req->uri)) {
        uint16_t uri_hash = dht_hash(req->uri, strlen(req->uri));
        fprintf(stderr, "DHT: URI '%s' hash = %d (0x%04x)\n", req->uri, uri_hash, uri_hash);
        
        // 检查我们是否负责这个 hash
        if (!is_responsible(uri_hash)) {
            // 我们不负责这个 hash
            
            // 检查 successor 是否负责
            if (successor_responsible(uri_hash)) {
                // Successor 负责 -> 303 重定向
                reply_len = (size_t)snprintf(buffer, sizeof(buffer),
                    "HTTP/1.1 303 See Other\r\n"
                    "Location: http://%s:%d%s\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n",
                    dht_state.successor.ip,
                    dht_state.successor.port,
                    req->uri);
                fprintf(stderr, "DHT: Redirecting to successor %s:%d\n",
                        dht_state.successor.ip, dht_state.successor.port);
                        
                if (send(conn, buffer, reply_len, 0) == -1) {
                    perror("send");
                }
                shutdown(conn, SHUT_RDWR);
                close(conn);
                return;
            }
            
            // 检查缓存中是否有结果
            if (dht_state.cache_valid) {
                // 有缓存结果 -> 303 重定向到缓存的负责节点
                reply_len = (size_t)snprintf(buffer, sizeof(buffer),
                    "HTTP/1.1 303 See Other\r\n"
                    "Location: http://%s:%d%s\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n",
                    dht_state.cached_responsible.ip,
                    dht_state.cached_responsible.port,
                    req->uri);
                fprintf(stderr, "DHT: Redirecting to cached peer %s:%d\n",
                        dht_state.cached_responsible.ip,
                        dht_state.cached_responsible.port);
                        
                // 清除缓存（一次性使用）
                dht_state.cache_valid = 0;
                
                if (send(conn, buffer, reply_len, 0) == -1) {
                    perror("send");
                }
                shutdown(conn, SHUT_RDWR);
                close(conn);
                return;
            }
            
            // 需要查找 -> 发送 lookup 并返回 503
            if (dht_state.successor.valid) {
                send_dht_message(dht_state.successor.ip,
                                dht_state.successor.port,
                                DHT_LOOKUP, uri_hash,
                                dht_state.self_id,
                                dht_state.self_ip,
                                dht_state.self_port);
            }
            
            // 返回 503 + Retry-After: 1
            reply = "HTTP/1.1 503 Service Unavailable\r\n"
                    "Retry-After: 1\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n";
            reply_len = strlen(reply);
            fprintf(stderr, "DHT: Returning 503 - lookup in progress\n");
            
            if (send(conn, reply, reply_len, 0) == -1) {
                perror("send");
            }
            shutdown(conn, SHUT_RDWR);
            close(conn);
            return;
        }
        
        // 我们负责这个 hash，继续正常处理
        fprintf(stderr, "DHT: We are responsible for hash %d\n", uri_hash);
    }

    /* ---------------- GET ---------------- */
    if (strcmp(req->method, "GET") == 0) {

        /*
         * GET 规则：
         *   1) /static/ 只能访问精确 foo/bar/baz，其他 /static/xxx -> 404
         *   2) /dynamic/ 只能是 /dynamic/<name>，否则 -> 404
         *   3) 其他路径：在 resources 里找，找不到 -> 404
         */

        // 1) static 前缀但不是三条之一：直接 404
        if (is_static_prefix(req->uri) && !is_static_exact(req->uri)) {
            reply = "HTTP/1.1 404 Not Found\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n";
            reply_len = strlen(reply);
        }
        // 2) dynamic 前缀但格式非法：直接 404
        else if (is_dynamic_prefix(req->uri) && !is_dynamic_valid(req->uri)) {
            reply = "HTTP/1.1 404 Not Found\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n";
            reply_len = strlen(reply);
        }
        // 3) 正常情况：去资源表里查
        else {
            size_t res_len = 0;
            const char *res = get(req->uri, resources, MAX_RESOURCES, &res_len);

            if (res != NULL) {
                // 找到资源：200 OK + Content-Length + body
                size_t header_len = (size_t)sprintf(
                    reply,
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Length: %lu\r\n"
                    "%s"
                    "\r\n",
                    (unsigned long)res_len,
                    conn_close_hdr);

                // body 放在 header 后面
                memcpy(reply + header_len, res, res_len);
                reply_len = header_len + res_len;
            } else {
                // 没找到：404
                reply = "HTTP/1.1 404 Not Found\r\n"
                        "Content-Length: 0\r\n"
                        "Connection: close\r\n"
                        "\r\n";
                reply_len = strlen(reply);
            }
        }
    }

    /* ---------------- PUT ---------------- */
    else if (strcmp(req->method, "PUT") == 0) {

        /*
         * PUT 规则（按作业要求）：
         *   - 只允许对 /dynamic/<name> 做 PUT
         *   - 如果 PUT 不是 /dynamic/... -> 403
         *   - 如果 /dynamic/... 格式非法 -> 404
         *   - PUT 必须有 body（payload），否则 -> 400
         *   - 创建新资源 -> 201 Created
         *   - 更新已有资源 -> 204 No Content
         */

        // 不是 /dynamic/ 开头：403
        if (!is_dynamic_prefix(req->uri)) {
            reply = "HTTP/1.1 403 Forbidden\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n";
            reply_len = strlen(reply);
        }
        // /dynamic/ 但格式非法（比如 /dynamic/ 或 /dynamic/a/b）：404
        else if (!is_dynamic_valid(req->uri)) {
            reply = "HTTP/1.1 404 Not Found\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n";
            reply_len = strlen(reply);
        }
        // payload 必须存在，否则 400
        else if (req->payload == NULL || req->payload_length < 0) {
            reply = "HTTP/1.1 400 Bad Request\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n";
            reply_len = strlen(reply);
        }
        else {
            /*
             * set():
             *   - 返回 true 表示"更新已有"
             *   - 返回 false 表示"新建"
             */
            if (set(req->uri, req->payload, req->payload_length, resources, MAX_RESOURCES)) {
                // 更新 -> 204
                reply = "HTTP/1.1 204 No Content\r\n"
                        "Content-Length: 0\r\n"
                        "Connection: close\r\n"
                        "\r\n";
            } else {
                // 新建 -> 201
                reply = "HTTP/1.1 201 Created\r\n"
                        "Content-Length: 0\r\n"
                        "Connection: close\r\n"
                        "\r\n";
            }
            reply_len = strlen(reply);
        }
    }

    /* ---------------- DELETE ---------------- */
    else if (strcmp(req->method, "DELETE") == 0) {

        /*
         * DELETE 规则：
         *   - 只允许 DELETE /dynamic/<name>
         *   - 不是 /dynamic/... -> 403
         *   - /dynamic/... 格式非法 -> 404（避免误删）
         *   - 删除成功 -> 204
         *   - 不存在 -> 404
         */

        // 非 /dynamic/：403
        if (!is_dynamic_prefix(req->uri)) {
            reply = "HTTP/1.1 403 Forbidden\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n";
            reply_len = strlen(reply);
        }
        // /dynamic/ 但不符合 /dynamic/<name>：404（关键：防止误删）
        else if (!is_dynamic_valid(req->uri)) {
            reply = "HTTP/1.1 404 Not Found\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n";
            reply_len = strlen(reply);
        }
        else {
            // 调用 data.c 的 delete() 删除资源
            if (delete(req->uri, resources, MAX_RESOURCES)) {
                reply = "HTTP/1.1 204 No Content\r\n"
                        "Content-Length: 0\r\n"
                        "Connection: close\r\n"
                        "\r\n";
            } else {
                reply = "HTTP/1.1 404 Not Found\r\n"
                        "Content-Length: 0\r\n"
                        "Connection: close\r\n"
                        "\r\n";
            }
            reply_len = strlen(reply);
        }
    }

    /* ---------------- other methods ---------------- */
    else {
        // 不支持的方法：501
        reply = "HTTP/1.1 501 Method Not Supported\r\n"
                "Content-Length: 0\r\n"
                "Connection: close\r\n"
                "\r\n";
        reply_len = strlen(reply);
    }

    /* 真正发送回复 */
    if (send(conn, reply, reply_len, 0) == -1) {
        // send 失败就打印错误并关闭连接
        perror("send");
        close(conn);
        return;
    }

    // 这里非常重要：我们明确关闭连接，保证每次请求都是新的连接
    shutdown(conn, SHUT_RDWR);
    close(conn);
}

/* =========================
 * 解析 buffer 里的一个请求
 * ========================= */

/*
 * handle_one_packet:
 *   - buf 里可能是一段 HTTP 数据（可能完整，也可能不完整）
 *   - parse_request() 会尝试解析出一个 request
 *
 * parse_request 返回值含义（skeleton 约定）：
 *   >0  : 成功解析出 1 个完整请求，返回"这个请求占用的字节数"
 *    0  : 数据不够，还需要继续 recv 更多数据
 *   -1  : 请求格式错误（malformed）
 *
 * 我们这里的策略：
 *   - 如果解析成功：立即回包并关闭连接，然后返回 -1 通知上层"这个连接结束了"
 *   - 如果解析错误：回 400 并关闭连接，然后返回 -1
 *   - 如果数据不够：返回 0
 */
static ssize_t handle_one_packet(int conn, char *buf, size_t n) {
    struct request req;
    req.method = NULL;
    req.uri = NULL;
    req.payload = NULL;
    req.payload_length = -1;

    ssize_t used = parse_request(buf, n, &req);

    if (used > 0) {
        // 成功解析 -> 回复 -> 连接结束
        send_reply_to_client(conn, &req);
        return -1;
    } else if (used == -1) {
        // 解析失败 -> 400
        const char *bad = "HTTP/1.1 400 Bad Request\r\n"
                          "Content-Length: 0\r\n"
                          "Connection: close\r\n"
                          "\r\n";
        send(conn, bad, strlen(bad), 0);
        shutdown(conn, SHUT_RDWR);
        close(conn);
        printf("Received malformed request, terminating connection.\n");
        return -1;
    }

    // used == 0：需要更多数据
    return used;
}

/* =========================
 * 连接状态管理（buffer）
 * ========================= */

/*
 * init_connection_state:
 *   skeleton 给了 connection_state 结构（里面有 buffer、end、sock）
 *   - sock：连接 fd
 *   - buffer：接收缓冲区
 *   - end：指向 buffer 中"已写入数据的末尾位置"
 */
static void init_connection_state(struct connection_state *st, int sock) {
    st->sock = sock;
    st->end = st->buffer;
    memset(st->buffer, 0, HTTP_MAX_SIZE);
}

/*
 * drop_front:
 *   把 buffer 前面已经处理掉的字节丢弃，剩下的挪到开头
 *   discard: 要丢弃多少字节
 *   keep   : 要保留多少字节
 */
static char *drop_front(char *buffer, size_t discard, size_t keep) {
    memmove(buffer, buffer + discard, keep);
    memset(buffer + keep, 0, discard);  // 把后面清掉，避免脏数据影响调试
    return buffer + keep;              // 返回新的 end 指针
}

/*
 * handle_connection_once:
 *   - 对某个已建立连接 socket 做一次 recv
 *   - 处理 buffer 里的请求（可能多次调用 handle_one_packet）
 *   - 因为我们策略是"一次请求就 close"，所以一般跑一次就结束连接
 *
 * 返回值：
 *   true  : 连接还可以继续（但本代码一般不会继续）
 *   false : 连接结束（或出错），上层要把 poll 恢复到监听状态
 */
static bool handle_connection_once(struct connection_state *st) {
    const char *buf_end = st->buffer + HTTP_MAX_SIZE;

    // 从 socket 读数据，写到 st->end 后面
    ssize_t r = recv(st->sock, st->end, (size_t)(buf_end - st->end), 0);
    if (r == -1) {
        perror("recv");
        close(st->sock);
        return false;
    }
    if (r == 0) {
        // 对方关闭连接
        close(st->sock);
        return false;
    }

    // window 是"当前待处理的数据窗口"
    char *win_start = st->buffer;
    char *win_end = st->end + r;

    // 只要还能解析出一个完整请求，就继续处理
    ssize_t used = 0;
    while ((used = handle_one_packet(st->sock, win_start,
                                     (size_t)(win_end - win_start))) > 0) {
        win_start += used;
    }

    // used == -1 表示连接已经关闭/应该结束
    if (used == -1) {
        return false;
    }

    // used == 0：请求还不完整，把剩余数据挪到 buffer 开头等待下一次 recv
    st->end = drop_front(st->buffer,
                         (size_t)(win_start - st->buffer),
                         (size_t)(win_end - win_start));
    return true;
}

/* =========================
 * 地址解析、建立 server socket
 * ========================= */

/*
 * make_addr:
 *   把 host/port 转成 sockaddr_in
 *   - host 可以是 127.0.0.1
 *   - port 是字符串形式，比如 "1235"
 */
static struct sockaddr_in make_addr(const char *host, const char *port) {
    struct addrinfo hints;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET; // 只用 IPv4

    struct addrinfo *res = NULL;
    int rc = getaddrinfo(host, port, &hints, &res);
    if (rc) {
        fprintf(stderr, "Error parsing host/port\n");
        exit(EXIT_FAILURE);
    }

    // 取第一条解析结果
    struct sockaddr_in out = *((struct sockaddr_in *)res->ai_addr);
    freeaddrinfo(res);
    return out;
}

/*
 * make_server_socket:
 *   建立 TCP server socket，bind + listen
 *   - 设置为 non-blocking，配合 poll
 *   - SO_REUSEADDR：避免端口 TIME_WAIT 导致 bind 失败
 */
static int make_server_socket(struct sockaddr_in addr) {
    const int enable = 1;
    const int backlog = 16;   // 允许排队的连接数

    int s = socket(AF_INET, SOCK_STREAM, 0);
    if (s == -1) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    // 设置非阻塞：accept 不会卡死
    if (fcntl(s, F_SETFL, O_NONBLOCK) == -1) {
        perror("fcntl");
        exit(EXIT_FAILURE);
    }

    // 允许地址复用
    if (setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(enable)) == -1) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    // 绑定 IP+端口
    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) == -1) {
        perror("bind");
        close(s);
        exit(EXIT_FAILURE);
    }

    // 开始监听
    if (listen(s, backlog)) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    return s;
}

/*
 * make_udp_socket:
 *   建立 UDP socket，bind 到同一个端口
 *   注意：不设置 SO_REUSEADDR，这样测试可以检测到端口已被占用
 */
static int make_udp_socket(struct sockaddr_in addr) {
    int s = socket(AF_INET, SOCK_DGRAM, 0);
    if (s == -1) {
        perror("udp socket");
        exit(EXIT_FAILURE);
    }

    // 设置非阻塞
    if (fcntl(s, F_SETFL, O_NONBLOCK) == -1) {
        perror("fcntl udp");
        exit(EXIT_FAILURE);
    }

    // 绑定 IP+端口
    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) == -1) {
        perror("bind udp");
        close(s);
        exit(EXIT_FAILURE);
    }

    return s;
}

/*
 * 读取环境变量初始化 DHT 状态
 */
static void init_dht_state(const char *self_ip, uint16_t self_port, int has_id, uint16_t self_id) {
    memset(&dht_state, 0, sizeof(dht_state));
    
    strncpy(dht_state.self_ip, self_ip, 15);
    dht_state.self_ip[15] = '\0';
    dht_state.self_port = self_port;
    dht_state.self_id = has_id ? self_id : 0;
    
    // 读取 predecessor 环境变量
    const char *pred_id = getenv("PRED_ID");
    const char *pred_ip = getenv("PRED_IP");
    const char *pred_port = getenv("PRED_PORT");
    
    if (pred_id && pred_ip && pred_port) {
        dht_state.predecessor.id = (uint16_t)atoi(pred_id);
        strncpy(dht_state.predecessor.ip, pred_ip, 15);
        dht_state.predecessor.ip[15] = '\0';
        dht_state.predecessor.port = (uint16_t)atoi(pred_port);
        dht_state.predecessor.valid = 1;
        fprintf(stderr, "DHT: Predecessor %d @ %s:%d\n",
                dht_state.predecessor.id,
                dht_state.predecessor.ip,
                dht_state.predecessor.port);
    }
    
    // 读取 successor 环境变量
    const char *succ_id = getenv("SUCC_ID");
    const char *succ_ip = getenv("SUCC_IP");
    const char *succ_port = getenv("SUCC_PORT");
    
    if (succ_id && succ_ip && succ_port) {
        dht_state.successor.id = (uint16_t)atoi(succ_id);
        strncpy(dht_state.successor.ip, succ_ip, 15);
        dht_state.successor.ip[15] = '\0';
        dht_state.successor.port = (uint16_t)atoi(succ_port);
        dht_state.successor.valid = 1;
        fprintf(stderr, "DHT: Successor %d @ %s:%d\n",
                dht_state.successor.id,
                dht_state.successor.ip,
                dht_state.successor.port);
    }
    
    fprintf(stderr, "DHT: Self %d @ %s:%d\n",
            dht_state.self_id,
            dht_state.self_ip,
            dht_state.self_port);
}

/* =========================
 * main：主循环
 * ========================= */

int main(int argc, char **argv) {
    /*
     * 程序运行方式：
     *   ./build/webserver self.ip self.port [node_id]
     * 例如：
     *   ./build/webserver 127.0.0.1 1235
     *   ./build/webserver 127.0.0.1 1235 16384
     */
    if (argc < 3 || argc > 4) {
        fprintf(stderr, "Usage: %s <ip> <port> [node_id]\n", argv[0]);
        return EXIT_FAILURE;
    }

    /*
     * 忽略 SIGPIPE：
     *   有时候客户端先断开连接，服务器 send() 会触发 SIGPIPE
     *   默认行为是直接杀死进程
     *   我们忽略它，让 send() 返回 -1，我们自己处理
     */
    signal(SIGPIPE, SIG_IGN);

    // 解析参数
    const char *self_ip = argv[1];
    uint16_t self_port = (uint16_t)atoi(argv[2]);
    int has_id = (argc == 4);
    uint16_t self_id = has_id ? (uint16_t)atoi(argv[3]) : 0;

    // 初始化 DHT 状态
    init_dht_state(self_ip, self_port, has_id, self_id);

    // 解析地址并创建 server socket
    struct sockaddr_in addr = make_addr(argv[1], argv[2]);
    int server_sock = make_server_socket(addr);
    
    // 创建 UDP socket (DHT)
    int udp_sock = make_udp_socket(addr);
    dht_state.udp_sock = udp_sock;
    
    fprintf(stderr, "Server listening on %s:%d (TCP + UDP)\n", self_ip, self_port);

    /*
     * pollfd 数组：
     *   fds[0]：监听 socket（server_sock）
     *   fds[1]：客户端连接 socket（一次只允许一个）
     *   fds[2]：UDP socket（DHT 消息）
     */
    struct pollfd fds[3];
    memset(fds, 0, sizeof(fds));
    fds[0].fd = server_sock;
    fds[0].events = POLLIN;
    fds[1].fd = -1;
    fds[1].events = 0;
    fds[2].fd = udp_sock;
    fds[2].events = POLLIN;

    // 单连接的状态结构体
    struct connection_state st;
    memset(&st, 0, sizeof(st));

    // 主循环：一直 poll 等事件
    while (true) {
        int ready = poll(fds, sizeof(fds) / sizeof(fds[0]), -1);
        if (ready == -1) {
            perror("poll");
            exit(EXIT_FAILURE);
        }

        // 处理 UDP (DHT) 消息
        if (fds[2].revents & POLLIN) {
            handle_dht_message();
        }

        // 遍历 TCP fd，看谁有事件
        for (size_t i = 0; i < 2; i++) {

            // 处理错误/挂起事件（客户端断开/异常）
            if (fds[i].revents & (POLLERR | POLLHUP | POLLNVAL)) {
                if (fds[i].fd != server_sock) {
                    // 关闭客户端 fd，并恢复监听
                    close(fds[i].fd);
                    fds[0].events = POLLIN;
                    fds[1].fd = -1;
                    fds[1].events = 0;
                }
                continue;
            }

            // 没有可读事件就跳过
            if (!(fds[i].revents & POLLIN)) {
                continue;
            }

            int s = fds[i].fd;

            // 如果是 server_sock 可读：说明有新连接可以 accept
            if (s == server_sock) {
                int conn = accept(server_sock, NULL, NULL);

                if (conn == -1) {
                    // 非阻塞模式下，没有连接时 accept 会返回 EAGAIN/EWOULDBLOCK
                    if (errno != EAGAIN && errno != EWOULDBLOCK) {
                        perror("accept");
                        exit(EXIT_FAILURE);
                    }
                } else {
                    // 初始化连接状态
                    init_connection_state(&st, conn);

                    // 有连接时，我们暂停接新连接（只处理一个）
                    fds[0].events = 0;
                    fds[1].fd = conn;
                    fds[1].events = POLLIN;
                }
            } else {
                // 否则就是客户端连接 socket 可读
                assert(s == st.sock);

                bool ok = handle_connection_once(&st);
                if (!ok) {
                    // 连接结束：重新恢复监听状态
                    fds[0].events = POLLIN;
                    fds[1].fd = -1;
                    fds[1].events = 0;
                }
            }
        }
    }

    return EXIT_SUCCESS;
}
