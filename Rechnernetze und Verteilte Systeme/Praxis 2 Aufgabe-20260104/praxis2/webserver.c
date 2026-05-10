#include <arpa/inet.h>     // inet_pton / inet_ntop
#include <assert.h>        // assert
#include <errno.h>         // errno / EAGAIN / EWOULDBLOCK
#include <fcntl.h>         // fcntl (设置非阻塞)
#include <netdb.h>         // getaddrinfo
#include <netinet/in.h>    // sockaddr_in
#include <poll.h>          // poll
#include <signal.h>        // signal(SIGPIPE, SIG_IGN)
#include <stdint.h>        // uint16_t 等
#include <stdio.h>         // printf / fprintf / perror
#include <stdlib.h>        // atoi / exit
#include <string.h>        // memset / memcpy / strcmp / strncpy
#include <sys/socket.h>    // socket / bind / listen / accept / send / recv / sendto / recvfrom
#include <sys/types.h>
#include <unistd.h>        // close / shutdown

#include "data.h"          // get/set/delete 资源表操作（skeleton 提供）
#include "http.h"          // parse_request + struct request（skeleton 提供）
#include "util.h"          // connection_state / HTTP_MAX_SIZE 等（skeleton 提供）

#define MAX_RESOURCES 100

/* --------------------
 * resources：资源表
 *
 * 这是一个数组，里面每一项是 (uri, 内容, 内容长度)
 * skeleton 的 data.c 会对这个数组做 get/set/delete
 *
 * 预置三个静态资源：
 *   /static/foo -> Foo
 *   /static/bar -> Bar
 *   /static/baz -> Baz
 *
 * 动态资源后续会通过 PUT /dynamic/xxx 写进去
 * -------------------- */
struct tuple resources[MAX_RESOURCES] = {
    {"/static/foo", "Foo", sizeof("Foo") - 1},
    {"/static/bar", "Bar", sizeof("Bar") - 1},
    {"/static/baz", "Baz", sizeof("Baz") - 1},
};

/* =========================================================
 * DHT（Chord）相关：常量、结构体、全局状态
 * ========================================================= */

/* UDP 消息 flags：本作业我们只用 LOOKUP 和 REPLY */
#define DHT_LOOKUP 0
#define DHT_REPLY  1

#pragma pack(push, 1)
/*
 * DHT UDP 消息格式（11 bytes），保持你的原逻辑：
 *   flags    : 1 byte
 *   hash     : 2 bytes  (网络序)
 *   peer_id  : 2 bytes  (网络序)
 *   peer_ip  : 4 bytes  (网络序)
 *   peer_port: 2 bytes  (网络序)
 *
 * LOOKUP：请求查询某个 hash 属于谁
 * REPLY ：返回“谁负责”
 */
struct dht_message { // dht_message是11字节
    uint8_t  flags;
    uint16_t hash;
    uint16_t peer_id;
    uint8_t  peer_ip[4];
    uint16_t peer_port;
};
#pragma pack(pop) //恢复默认对齐，避免结构体对齐带来的问题，#是预处理指令，pop是恢复之前的对齐方式，pragma的作用是告诉编译器如何处理特定的代码段，避免结构体对齐带来的问题，他能保证结构体按照1字节对齐

/* 保存一个节点的信息（id + ip + port） */
struct peer_info { //peer_info是24字节,里面有id，ip，port，valid四个成员变量，分别表示节点ID，IP地址，端口号和有效性标志，分别是2字节，16字节，2字节，4字节
    uint16_t id;
    char ip[16];      // IPv4 字符串最多 15 字符 + '\0'
    uint16_t port;
    int valid;        // 1 表示有效，0 表示未设置
};

/*
 * 全局 DHT 状态（初学者风格：直接用全局变量）
 *
 * self：当前节点信息
 * predecessor / successor：前驱和后继（通过环境变量读入）
 *
 * cache：一次性缓存（你当前逻辑就是：收到 reply 就存一下，下次用完清掉）
 */
static struct { // 分别表示DHT状态的结构体，包含当前节点ID，IP地址，端口号，前驱节点信息，后继节点信息，UDP套接字，缓存的哈希值，缓存的负责节点信息和缓存有效性标志，字节量分别为2字节，16字节，2字节，24字节，24字节，4字节，2字节，24字节，4字节
    uint16_t self_id;                  // 当前节点 ID，通过命令行参数传入，默认 0，最大字节量为2字节
    char self_ip[16];           // 当前节点 IP 地址，字符串形式，最多 15 字符 + '\0'，字节量为16字节    
    uint16_t self_port;               // 当前节点端口号，字节量为2字节

    struct peer_info predecessor; // 前驱节点信息，字节量为24字节
    struct peer_info successor;   // 后继节点信息，字节量为24字节

    int udp_sock;                   // UDP socket，用于 DHT 消息收发，字节量为4字节

    uint16_t cached_hash;                 // 其实你当前逻辑不会严格用它校验，但保留一下，字节量为2字节
    struct peer_info cached_responsible;  // 缓存的“负责节点”，字节量为24字节
    int cache_valid;                      // 1 表示缓存可用，0 表示无效，字节量为4字节
} dht_state;

/* =========================================================
 * URI 判断：static/dynamic 规则
 * ========================================================= */

/* 判断是否以 /static/ 开头 */
static int is_static_prefix(const char *uri) { 
    return (strncmp(uri, "/static/", 8) == 0);
}

/* 判断是否以 /dynamic/ 开头 */
static int is_dynamic_prefix(const char *uri) {
    return (strncmp(uri, "/dynamic/", 9) == 0);
}

/*
 * 静态资源只允许精确三条：
 *   /static/foo  /static/bar  /static/baz
 * 其它像 /static/abc 一律 404
 */
static int is_static_exact(const char *uri) {
    if (strcmp(uri, "/static/foo") == 0) return 1;
    if (strcmp(uri, "/static/bar") == 0) return 1;
    if (strcmp(uri, "/static/baz") == 0) return 1;
    return 0;
}

/*
 * 动态资源合法格式：
 *   /dynamic/<name>
 *
 * 不合法：
 *   /dynamic/            (name 为空)
 *   /dynamic/a/b         (多层路径)
 *
 * 这样做的目的：
 *   防止出现 /dynamic/hello/hello 这种路径在 delete/get 时被误匹配
 */
static int is_dynamic_valid(const char *uri) {
    if (!is_dynamic_prefix(uri)) return 0;

    const char *name = uri + 9; /* 跳过 "/dynamic/" */
    if (*name == '\0') return 0;              /* 后面不能为空 */
    if (strchr(name, '/') != NULL) return 0;  /* name 里不允许再出现 '/' */
    return 1;
}

/* =========================================================
 * 哈希函数（必须与测试一致）
 * ========================================================= */

/*
 * dht_hash：你现在用的是“类似 checksum 的 16-bit hash”
 * - 每两个字节当成一个 16-bit word 相加
 * - 最后折叠进位
 * - 取反
 *
 * 注意：这是为了和测试用例一致，不要随便改算法
 */
static uint16_t dht_hash(const char *data, size_t len) {
    uint32_t sum = 0;

    /* 每两个字节处理一次 */
    for (size_t i = 0; i < len; i += 2) {
        uint16_t word = 0;
        if (i + 1 < len) {
            /* 两个字节凑一个 16-bit：高字节在前 */
            word = ((uint8_t)data[i] << 8) | (uint8_t)data[i + 1]; // ｜是按位或运算符
        } else {
            /* 奇数长度：最后一个字节补 0 */
            word = ((uint8_t)data[i] << 8);
        }
        sum += word;
    }

    /* 折叠高 16-bit 的进位 */
    sum = (sum & 0xffff) + (sum >> 16);

    /* 取反并截断为 16-bit */
    sum = ~sum & 0xffff; //～是按位取反运算符

    return (uint16_t)sum;
}

/* =========================================================
 * DHT 环判断：responsible / successor_responsible
 * ========================================================= */

/*
 * is_responsible：
 * 判断 hash h 是否属于当前节点负责的区间：(pred, self]
 *
 * 环形区间规则：
 * - 如果 pred < self：正常区间 (pred, self]
 * - 如果 pred > self：跨 0，区间是 (pred, 65535] ∪ [0, self]
 * - 如果没有 predecessor（pred 未设置）：你当前逻辑是 self 负责全部
 */
static int is_responsible(uint16_t h) {
    if (!dht_state.predecessor.valid) {
        return 1;
    }

    uint16_t pred = dht_state.predecessor.id;
    uint16_t self = dht_state.self_id;

    if (pred < self) {
        return (pred < h && h <= self);
    } else {
        return (h > pred || h <= self);
    }
}

/*
 * successor_responsible：
 * 判断 h 是否属于 successor 的区间：(self, succ]
 * 用来快速判断：如果 succ 负责，就直接 303 重定向过去
 */
static int successor_responsible(uint16_t h) {
    if (!dht_state.successor.valid) return 0;

    uint16_t self = dht_state.self_id;
    uint16_t succ = dht_state.successor.id;

    if (self < succ) {
        return (self < h && h <= succ);
    } else {
        return (h > self || h <= succ);
    }
}

/* =========================================================
 * UDP：发送 DHT 消息
 * ========================================================= */

/*
 * send_dht_message：
 * 向某个 dest_ip:dest_port 发送一个 DHT UDP 消息
 *
 * 参数解释：
 * - flags：LOOKUP / REPLY
 * - hash ：要查询的 hash 或者 reply 里携带的字段（保持你原逻辑）
 * - peer_id/peer_ip/peer_port：放进消息体里给对方用
 */
static void send_dht_message(const char *dest_ip, uint16_t dest_port,
                            uint8_t flags, uint16_t hash,
                            uint16_t peer_id, const char *peer_ip, uint16_t peer_port) {
    struct dht_message msg;
    memset(&msg, 0, sizeof(msg));

    msg.flags = flags;
    msg.hash = htons(hash);
    msg.peer_id = htons(peer_id);
    msg.peer_port = htons(peer_port);

    /* peer_ip 字符串 -> 4 字节网络序 */
    struct in_addr tmp; // in_addr 结构体用于存储IPv4地址,tmp是一个临时变量
    inet_pton(AF_INET, peer_ip, &tmp); //inet_pton函数用于将IP地址从文本字符串格式转换为网络字节序的二进制格式
    memcpy(msg.peer_ip, &tmp.s_addr, 4); // memcpy函数用于将peer_ip的前4个字节复制到msg.peer_ip中

    /* 目标地址 */
    struct sockaddr_in dest; // sockaddr_in 结构体用于存储IPv4地址和端口号信息,dest是目标地址变量
    memset(&dest, 0, sizeof(dest)); //将dest结构体的所有字节初始化为0, memset函数用于初始化内存块
    dest.sin_family = AF_INET; // AF_INET 表示使用 IPv4 地址族
    dest.sin_port = htons(dest_port); // htons函数用于将主机字节序转换为网络字节序
    inet_pton(AF_INET, dest_ip, &dest.sin_addr); //将目标IP地址从文本字符串格式转换为网络字节序的二进制格式，并存储在dest.sin_addr中

    /* 发 UDP */
    (void)sendto(dht_state.udp_sock, &msg, sizeof(msg), 0, //发送UDP数据报到指定的目标地址
                 (struct sockaddr *)&dest, sizeof(dest)); // sendto函数用于发送UDP数据报

    fprintf(stderr, "DHT: send flags=%d hash=%u to %s:%u\n",
            (int)flags, (unsigned)hash, dest_ip, (unsigned)dest_port);
}

/* =========================================================
 * UDP：接收并处理 DHT 消息（LOOKUP/REPLY）
 * ========================================================= */

/*
 * handle_dht_message：
 * 从 udp_sock 上读一个消息出来处理
 *
 * 处理逻辑保持你原来的：
 * - 收到 LOOKUP：
 *     如果 successor 负责这个 hash -> 给请求者发 REPLY（告诉他 successor）
 *     否则转发给 successor
 * - 收到 REPLY：
 *     缓存一份负责节点（一次性缓存）
 */
static void handle_dht_message(void) {
    struct dht_message msg;
    struct sockaddr_in sender;
    socklen_t sl = sizeof(sender);

    ssize_t n = recvfrom(dht_state.udp_sock, &msg, sizeof(msg), 0,
                         (struct sockaddr *)&sender, &sl);
    if (n != (ssize_t)sizeof(msg)) { //ssize_t是无符号类型，ssize_t是有符号类型
        fprintf(stderr, "DHT: bad udp size %zd\n", n); //%zd用于打印ssize_t类型的变量,stderr是标准错误输出流, fprintf函数用于格式化输出到指定的输出流
        return;
    }

    uint8_t flags = msg.flags;
    uint16_t hash = ntohs(msg.hash); // ntohs函数用于将网络字节序转换为主机字节序
    uint16_t peer_id = ntohs(msg.peer_id);
    uint16_t peer_port = ntohs(msg.peer_port);

    /* 解析 peer_ip */
    struct in_addr a;
    memcpy(&a.s_addr, msg.peer_ip, 4);
    char peer_ip[16];
    inet_ntop(AF_INET, &a, peer_ip, sizeof(peer_ip)); // inet_ntop函数用于将网络字节序的二进制格式转换为文本字符串格式

    fprintf(stderr, "DHT: recv flags=%d hash=%u peer=%u %s:%u\n",
            (int)flags, (unsigned)hash, (unsigned)peer_id, peer_ip, (unsigned)peer_port);

    if (flags == DHT_LOOKUP) {
        /*
         * LOOKUP：peer_ip:peer_port 是“原始请求者”
         * 这里我们只判断 successor 是否负责
         */
        if (successor_responsible(hash)) {
            /*
             * 发送 REPLY 给请求者
             * 注意：reply 里 hash 字段你原逻辑传的是 self_id（不改）
             * peer_id/peer_ip/peer_port 填 successor 的信息（告诉请求者去哪）
             */
            send_dht_message(peer_ip, peer_port,
                             DHT_REPLY, dht_state.self_id,
                             dht_state.successor.id,
                             dht_state.successor.ip,
                             dht_state.successor.port);
        } else {
            /* 不负责就转发给 successor */
            if (dht_state.successor.valid) {
                send_dht_message(dht_state.successor.ip,
                                 dht_state.successor.port,
                                 DHT_LOOKUP, hash,
                                 peer_id, peer_ip, peer_port);
            }
        }
    } else if (flags == DHT_REPLY) {
        /* REPLY：缓存负责节点（一次性） */
        fprintf(stderr, "DHT: reply says responsible=%u %s:%u\n",
                (unsigned)peer_id, peer_ip, (unsigned)peer_port);

        dht_state.cached_hash = hash;
        dht_state.cached_responsible.id = peer_id;
        strncpy(dht_state.cached_responsible.ip, peer_ip, 15);
        dht_state.cached_responsible.ip[15] = '\0';
        dht_state.cached_responsible.port = peer_port;
        dht_state.cached_responsible.valid = 1;

        dht_state.cache_valid = 1;
    } else {
        fprintf(stderr, "DHT: unknown flags=%d\n", (int)flags);
    }
}

/* =========================================================
 * HTTP：核心处理（先 DHT 路由，再本地 GET/PUT/DELETE）
 * ========================================================= */

/*
 * send_reply_to_client：
 * 1) 先判断是否需要走 DHT（非 /static/）
 *    - 如果本节点不负责：可能 303 / 503
 *    - 如果本节点负责：继续走本地资源表
 * 2) 本地规则：
 *    - GET:
 *        /static/ 只能 foo/bar/baz，否则 404
 *        /dynamic/ 必须合法一层，否则 404
 *    - PUT/DELETE:
 *        只能对 /dynamic/<name> 操作
 *        PUT 非 dynamic -> 403
 *        PUT dynamic 但非法 -> 404
 *        DELETE 非 dynamic -> 403
 *        DELETE dynamic 但非法 -> 404
 *
 * 注意：每次都 Connection: close，并且 shutdown+close
 */
static void send_reply_to_client(int conn, struct request *req) {
    char buffer[HTTP_MAX_SIZE];
    char *reply = buffer;
    size_t reply_len = 0;

    fprintf(stderr, "Handling %s %s (payload=%lu)\n",
            req->method, req->uri, (unsigned long)req->payload_length); //req->method是请求方法，req->uri是请求的URI，req->payload_length是请求负载的长度

    /* =======================
     * 先做 DHT 路由（非 static）
     * ======================= */
    if (!is_static_prefix(req->uri)) { // 非 static 资源需要 DHT 路由
        uint16_t h = dht_hash(req->uri, strlen(req->uri));// 计算URI的哈希值,dht_hash函数用于计算URI的哈希值,strlen函数用于计算字符串的长度
        fprintf(stderr, "DHT: uri hash=%u\n", (unsigned)h);

        /* 如果我不负责这个 hash，就不要在本地资源表上操作 */
        if (!is_responsible(h)) {

            /* 1) successor 负责 => 直接 303 */
            if (successor_responsible(h)) {
                int n = snprintf(buffer, sizeof(buffer),
                                 "HTTP/1.1 303 See Other\r\n"
                                 "Location: http://%s:%u%s\r\n"
                                 "Content-Length: 0\r\n"
                                 "Connection: close\r\n"
                                 "\r\n",
                                 dht_state.successor.ip,
                                 (unsigned)dht_state.successor.port,
                                 req->uri);
                if (n > 0) {
                    (void)send(conn, buffer, (size_t)n, 0);
                }
                shutdown(conn, SHUT_RDWR);
                close(conn);
                return;
            }

            /* 2) 有缓存 => 303（你原逻辑不校验 hash，我也不加） */
            if (dht_state.cache_valid) {
                int n = snprintf(buffer, sizeof(buffer),
                                 "HTTP/1.1 303 See Other\r\n"
                                 "Location: http://%s:%u%s\r\n"
                                 "Content-Length: 0\r\n"
                                 "Connection: close\r\n"
                                 "\r\n",
                                 dht_state.cached_responsible.ip,
                                 (unsigned)dht_state.cached_responsible.port,
                                 req->uri);

                /* 一次性缓存：用完清掉 */
                dht_state.cache_valid = 0;

                if (n > 0) {
                    (void)send(conn, buffer, (size_t)n, 0);
                }
                shutdown(conn, SHUT_RDWR);
                close(conn);
                return;
            }

            /* 3) 没有缓存也不是 succ 负责 => 发 lookup 给 succ，然后回 503 */
            if (dht_state.successor.valid) {
                send_dht_message(dht_state.successor.ip,
                                 dht_state.successor.port,
                                 DHT_LOOKUP, h,
                                 dht_state.self_id,
                                 dht_state.self_ip,
                                 dht_state.self_port);
            }

            reply =
                "HTTP/1.1 503 Service Unavailable\r\n"
                "Retry-After: 1\r\n"
                "Content-Length: 0\r\n"
                "Connection: close\r\n"
                "\r\n";
            reply_len = strlen(reply);

            (void)send(conn, reply, reply_len, 0);
            shutdown(conn, SHUT_RDWR);
            close(conn);
            return;
        }
    }

    /* =======================
     * 本地 HTTP 处理
     * ======================= */

    if (strcmp(req->method, "GET") == 0) {
        /*
         * GET:
         *  - /static/xxx 只能 foo/bar/baz，否则 404
         *  - /dynamic/xxx 必须合法一层，否则 404
         *  - 其它：直接 get() 查资源表
         */
        if (is_static_prefix(req->uri) && !is_static_exact(req->uri)) { //is_static_prefix函数用于判断URI是否以/static/开头，is_static_exact函数用于判断静态资源的合法性
            reply =
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Length: 0\r\n"
                "Connection: close\r\n"
                "\r\n";
            reply_len = strlen(reply); //strlen函数用于计算字符串的长度
        } else if (is_dynamic_prefix(req->uri) && !is_dynamic_valid(req->uri)) { //is_dynamic_prefix函数用于判断URI是否以/dynamic/开头，is_dynamic_valid函数用于判断动态资源的合法性
            reply =
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Length: 0\r\n"
                "Connection: close\r\n"
                "\r\n";
            reply_len = strlen(reply); 
        } else {
            size_t res_len = 0;
            const char *res = get(req->uri, resources, MAX_RESOURCES, &res_len); //get函数用于从资源表中获取指定URI的资源内容和长度

            if (res) {
                /*
                 * 200 OK：先写 header，再 memcpy body
                 * （HTTP_MAX_SIZE 够大，正常不会溢出）
                 */
                int header_n = snprintf(buffer, sizeof(buffer), //snprintf函数用于将格式化的数据写入字符串buffer中
                                        "HTTP/1.1 200 OK\r\n"
                                        "Content-Length: %lu\r\n"
                                        "Connection: close\r\n"
                                        "\r\n",
                                        (unsigned long)res_len);
                if (header_n < 0) header_n = 0;

                if ((size_t)header_n + res_len <= sizeof(buffer)) {
                    memcpy(buffer + header_n, res, res_len);
                    reply_len = (size_t)header_n + res_len;
                    (void)send(conn, buffer, reply_len, 0);
                } else {
                    /* 理论上不会发生，但这里简单处理一下 */
                    (void)send(conn, buffer, (size_t)header_n, 0);
                }

                shutdown(conn, SHUT_RDWR);
                close(conn);
                return;
            } else {
                reply =
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n";
                reply_len = strlen(reply);
            }
        }
    } else if (strcmp(req->method, "PUT") == 0) {
        /*
         * PUT:
         *  - 非 /dynamic/ -> 403
         *  - /dynamic/ 但非法 -> 404
         *  - 没有 payload -> 400
         *  - set() 返回 true 表示更新 -> 204
         *  - set() 返回 false 表示新建 -> 201
         */
        if (!is_dynamic_prefix(req->uri)) {
            reply =
                "HTTP/1.1 403 Forbidden\r\n"
                "Content-Length: 0\r\n"
                "Connection: close\r\n"
                "\r\n";
            reply_len = strlen(reply);
        } else if (!is_dynamic_valid(req->uri)) {
            reply =
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Length: 0\r\n"
                "Connection: close\r\n"
                "\r\n";
            reply_len = strlen(reply);
        } else if (req->payload == NULL || req->payload_length < 0) {
            reply =
                "HTTP/1.1 400 Bad Request\r\n"
                "Content-Length: 0\r\n"
                "Connection: close\r\n"
                "\r\n";
            reply_len = strlen(reply);
        } else {
            if (set(req->uri, req->payload, req->payload_length, resources, MAX_RESOURCES)) {
                reply =
                    "HTTP/1.1 204 No Content\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n";
            } else {
                reply =
                    "HTTP/1.1 201 Created\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n";
            }
            reply_len = strlen(reply);
        }
    } else if (strcmp(req->method, "DELETE") == 0) {
        /*
         * DELETE:
         *  - 非 /dynamic/ -> 403
         *  - /dynamic/ 但非法 -> 404（防误删）
         *  - delete() 成功 -> 204
         *  - delete() 失败 -> 404
         */
        if (!is_dynamic_prefix(req->uri)) {
            reply =
                "HTTP/1.1 403 Forbidden\r\n"
                "Content-Length: 0\r\n"
                "Connection: close\r\n"
                "\r\n";
            reply_len = strlen(reply);
        } else if (!is_dynamic_valid(req->uri)) {
            reply =
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Length: 0\r\n"
                "Connection: close\r\n"
                "\r\n";
            reply_len = strlen(reply);
        } else {
            if (delete(req->uri, resources, MAX_RESOURCES)) { //delete函数用于从资源表中删除指定URI的资源
                reply =
                    "HTTP/1.1 204 No Content\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n";
            } else {
                reply =
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n";
            }
            reply_len = strlen(reply);
        }
    } else {
        /* 其它方法：501 */
        reply =
            "HTTP/1.1 501 Method Not Supported\r\n"
            "Content-Length: 0\r\n"
            "Connection: close\r\n"
            "\r\n";
        reply_len = strlen(reply);
    }

    /* 统一发送并关闭连接 */
    (void)send(conn, reply, reply_len, 0);
    shutdown(conn, SHUT_RDWR); // 关闭读写
    close(conn); // 关闭 socket
}

/* =========================================================
 * 处理一个 HTTP 请求包（一次请求就关闭连接）
 * ========================================================= */

/*
 * handle_one_packet：
 * parse_request(buf, n, &req) 的返回值含义：
 *  >0：成功解析出 1 个完整请求，占用 used 字节
 *   0：数据不够，需要继续 recv
 *  -1：请求格式错误
 *
 * 我们的策略：解析成功就回包并关连接，返回 -1 告诉上层“连接结束”
 */
static ssize_t handle_one_packet(int conn, char *buf, size_t n) {
    struct request req;
    req.method = NULL;
    req.uri = NULL;
    req.payload = NULL;
    req.payload_length = -1;

    ssize_t used = parse_request(buf, n, &req); // parse_request函数用于解析HTTP请求报文,返回值表示解析结果
    if (used > 0) {
        send_reply_to_client(conn, &req); // send_reply_to_client函数用于根据解析结果发送HTTP响应报文给客户端
        return -1;
    }
    if (used == -1) {
        const char *bad =
            "HTTP/1.1 400 Bad Request\r\n"
            "Content-Length: 0\r\n"
            "Connection: close\r\n"
            "\r\n";
        (void)send(conn, bad, strlen(bad), 0);
        shutdown(conn, SHUT_RDWR);
        close(conn);
        return -1;
    }
    return 0; /* used == 0：还需要更多数据 */
}

/* =========================================================
 * skeleton 的连接缓冲区处理
 * ========================================================= */

/* 初始化 connection_state（skeleton 提供的结构） */
static void init_connection_state(struct connection_state *st, int sock) { //init_connection_state函数用于初始化连接状态结构体connection_state
    st->sock = sock;
    st->end = st->buffer;
    memset(st->buffer, 0, HTTP_MAX_SIZE); //memset函数用于将连接状态结构体connection_state的缓冲区buffer初始化为0
}

/*
 * drop_front：
 * 把 buffer 前面 discard 的字节丢掉，把剩余 keep 字节挪到 buffer 开头
 */
static char *drop_front(char *buffer, size_t discard, size_t keep) {
    memmove(buffer, buffer + discard, keep); //memmove函数用于将缓冲区buffer中从discard位置开始的keep字节移动到缓冲区的开头
    memset(buffer + keep, 0, discard); //memset函数用于将缓冲区buffer中从keep位置开始的discard字节初始化为0
    return buffer + keep;
}

/*
 * handle_connection_once：
 * 对一个 TCP 连接做一次 recv，然后尝试解析请求
 * 因为我们每次请求都 close，所以通常一次就结束
 */
static bool handle_connection_once(struct connection_state *st) {
    const char *buf_end = st->buffer + HTTP_MAX_SIZE;

    ssize_t r = recv(st->sock, st->end, (size_t)(buf_end - st->end), 0);
    if (r <= 0) {
        close(st->sock);
        return false;
    }

    char *win_start = st->buffer;
    char *win_end = st->end + r;

    ssize_t used = 0;
    while ((used = handle_one_packet(st->sock, win_start, (size_t)(win_end - win_start))) > 0) {
        win_start += used;
    }

    if (used == -1) return false;

    st->end = drop_front(st->buffer, //drop_front函数用于丢弃连接状态结构体connection_state的缓冲区buffer中前面已经处理过的字节，并将剩余的字节移动到缓冲区的开头
                         (size_t)(win_start - st->buffer),
                         (size_t)(win_end - win_start));
    return true;
}

/* =========================================================
 * 建立 TCP/UDP socket
 * ========================================================= */

/* host+port -> sockaddr_in */
static struct sockaddr_in make_addr(const char *host, const char *port) { //make_addr函数用于根据主机名和端口号创建一个sockaddr_in结构体
    struct addrinfo hints;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;

    struct addrinfo *res = NULL;
    int rc = getaddrinfo(host, port, &hints, &res); //getaddrinfo函数用于根据主机名和端口号获取地址信息,返回值表示函数执行结果
    if (rc) {
        fprintf(stderr, "getaddrinfo failed\n");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_in out = *((struct sockaddr_in *)res->ai_addr);
    freeaddrinfo(res); //freeaddrinfo函数用于释放由getaddrinfo函数分配的地址信息结构体
    return out;
}

/* 建立 TCP server socket：non-blocking + reuseaddr + bind + listen */
static int make_server_socket(struct sockaddr_in addr) {
    int s = socket(AF_INET, SOCK_STREAM, 0);
    if (s == -1) { perror("socket"); exit(EXIT_FAILURE); } //perror函数用于打印错误信息,EXIT_FAILURE表示程序执行失败的退出状态码

    if (fcntl(s, F_SETFL, O_NONBLOCK) == -1) { perror("fcntl"); exit(EXIT_FAILURE); } //fcntl函数用于设置文件描述符的属性,O_NONBLOCK表示设置为非阻塞模式

    int enable = 1;
    if (setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(enable)) == -1) { //setsockopt函数用于设置套接字选项,SOL_SOCKET表示设置套接字级别的选项,SO_REUSEADDR表示允许重用本地地址
        perror("setsockopt"); 
        exit(EXIT_FAILURE);
    }

    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) == -1) { perror("bind"); exit(EXIT_FAILURE); } //bind函数用于将套接字绑定到指定的地址和端口号
    if (listen(s, 16) == -1) { perror("listen"); exit(EXIT_FAILURE); } //listen函数用于将套接字设置为监听状态,16表示监听队列的最大长度
    return s;
}

/* 建立 UDP socket：non-blocking + bind 到同端口（用于 DHT） */
static int make_udp_socket(struct sockaddr_in addr) {
    int s = socket(AF_INET, SOCK_DGRAM, 0);
    if (s == -1) {
        perror("socket(udp)");
        exit(EXIT_FAILURE);
    }

    // 非阻塞（配合 poll）
    if (fcntl(s, F_SETFL, O_NONBLOCK) == -1) { //fcntl函数用于设置文件描述符的属性,O_NONBLOCK表示设置为非阻塞模式
        perror("fcntl(udp)");
        close(s);
        exit(EXIT_FAILURE);
    }

    // 关键：bind 到传进来的 addr（比如 127.0.0.1），不要改成 INADDR_ANY
    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) == -1) {
        perror("bind(udp)");
        close(s);
        exit(EXIT_FAILURE);
    }

    return s;
}


/* =========================================================
 * 初始化 DHT 状态：读取环境变量
 * ========================================================= */

/*
 * init_dht_state：
 * 从环境变量读取 predecessor/successor：
 *   PRED_ID PRED_IP PRED_PORT
 *   SUCC_ID SUCC_IP SUCC_PORT
 *
 * self_id 可从命令行 argv[3] 传入，若没有则默认 0
 */
static void init_dht_state(const char *self_ip, uint16_t self_port, int has_id, uint16_t self_id) { //init_dht_state函数用于初始化DHT状态结构体dht_state
    memset(&dht_state, 0, sizeof(dht_state));

    strncpy(dht_state.self_ip, self_ip, 15);
    dht_state.self_ip[15] = '\0';
    dht_state.self_port = self_port;
    dht_state.self_id = has_id ? self_id : 0;

    /* predecessor */
    const char *pred_id = getenv("PRED_ID"); //getenv函数用于获取环境变量的值
    const char *pred_ip = getenv("PRED_IP");
    const char *pred_port = getenv("PRED_PORT");
    if (pred_id && pred_ip && pred_port) {
        dht_state.predecessor.id = (uint16_t)atoi(pred_id); //atoi函数用于将字符串转换为整数
        strncpy(dht_state.predecessor.ip, pred_ip, 15);
        dht_state.predecessor.ip[15] = '\0';
        dht_state.predecessor.port = (uint16_t)atoi(pred_port);
        dht_state.predecessor.valid = 1;
    }

    /* successor */
    const char *succ_id = getenv("SUCC_ID");
    const char *succ_ip = getenv("SUCC_IP");
    const char *succ_port = getenv("SUCC_PORT");
    if (succ_id && succ_ip && succ_port) {
        dht_state.successor.id = (uint16_t)atoi(succ_id);
        strncpy(dht_state.successor.ip, succ_ip, 15);
        dht_state.successor.ip[15] = '\0';
        dht_state.successor.port = (uint16_t)atoi(succ_port);
        dht_state.successor.valid = 1;
    }

    fprintf(stderr, "DHT: self=%u %s:%u\n",  //%u用于打印无符号整数,%s用于打印字符串,stderr是标准错误输出流, fprintf函数用于格式化输出到指定的输出流
            (unsigned)dht_state.self_id, dht_state.self_ip, (unsigned)dht_state.self_port);
    if (dht_state.predecessor.valid) {
        fprintf(stderr, "DHT: pred=%u %s:%u\n",
                (unsigned)dht_state.predecessor.id,
                dht_state.predecessor.ip,
                (unsigned)dht_state.predecessor.port);
    }
    if (dht_state.successor.valid) {
        fprintf(stderr, "DHT: succ=%u %s:%u\n",
                (unsigned)dht_state.successor.id,
                dht_state.successor.ip,
                (unsigned)dht_state.successor.port);
    }
}

/* =========================================================
 * main：poll 监听 TCP + UDP
 * ========================================================= */





int main(int argc, char **argv) {
    if (argc < 3 || argc > 4) {
        fprintf(stderr, "Usage: %s <ip> <port> [node_id]\n", argv[0]);
        return EXIT_FAILURE;
    }

    signal(SIGPIPE, SIG_IGN);

    const char *self_ip = argv[1];
    uint16_t self_port = (uint16_t)atoi(argv[2]);
    int has_id = (argc == 4);
    uint16_t self_id = has_id ? (uint16_t)atoi(argv[3]) : 0;

    /* 初始化 DHT（读 env） */
    init_dht_state(self_ip, self_port, has_id, self_id);

    /* ✅这两行你这段里缺了：先把 addr 和 server_sock 搞出来 */
    struct sockaddr_in addr = make_addr(argv[1], argv[2]);
    int server_sock = make_server_socket(addr);

    /* ✅UDP socket：这里只调用，不要在 main 里定义函数 */
    int udp_sock = make_udp_socket(addr);
    dht_state.udp_sock = udp_sock;

    fprintf(stderr, "Server up on %s:%u (tcp+udp)\n", self_ip, (unsigned)self_port);

    struct pollfd fds[3];
    memset(fds, 0, sizeof(fds));

    fds[0].fd = server_sock;
    fds[0].events = POLLIN;

    fds[1].fd = -1;
    fds[1].events = 0;

    fds[2].fd = udp_sock;
    fds[2].events = POLLIN;

    struct connection_state st;
    memset(&st, 0, sizeof(st));

    while (true) {
        int ready = poll(fds, 3, -1);
        if (ready == -1) {
            perror("poll");
            exit(EXIT_FAILURE);
        }

        if (fds[2].revents & POLLIN) {
            handle_dht_message();
        }

        for (int i = 0; i < 2; i++) {
            if (fds[i].revents & (POLLERR | POLLHUP | POLLNVAL)) {
                if (fds[i].fd != server_sock) {
                    close(fds[i].fd);
                    fds[0].events = POLLIN;
                    fds[1].fd = -1;
                    fds[1].events = 0;
                }
                continue;
            }

            if (!(fds[i].revents & POLLIN)) continue;

            if (fds[i].fd == server_sock) {
                int conn = accept(server_sock, NULL, NULL);
                if (conn == -1) {
                    if (errno != EAGAIN && errno != EWOULDBLOCK) {
                        perror("accept");
                        exit(EXIT_FAILURE);
                    }
                } else {
                    init_connection_state(&st, conn);
                    fds[0].events = 0;
                    fds[1].fd = conn;
                    fds[1].events = POLLIN;
                }
            } else {
                assert(fds[i].fd == st.sock);
                bool ok = handle_connection_once(&st);
                if (!ok) {
                    fds[0].events = POLLIN;
                    fds[1].fd = -1;
                    fds[1].events = 0;
                }
            }
        }
    }

    return EXIT_SUCCESS;
}