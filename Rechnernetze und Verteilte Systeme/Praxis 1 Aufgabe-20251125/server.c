#define _GNU_SOURCE
#include <arpa/inet.h>
#include <ctype.h>
#include <errno.h>
#include <netdb.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#define BACKLOG 16
#define RECV_BUF_SIZE 8192
#define MAX_HEADERS 40
#define MAX_HEADER_LEN 256
#define MAX_RESOURCES 100

static volatile sig_atomic_t g_stop = 0;  // 用于标识是否收到停止信号

// HTTP 响应状态码结构体
typedef struct {
    int code;       // 状态码
    const char* msg; // 状态描述
} Status; 

// HTTP 响应状态列表
static const Status status_list[] = {
    {200, "OK"},
    {201, "Created"},
    {204, "No Content"},
    {400, "Bad Request"},
    {403, "Forbidden"},
    {404, "Not Found"},
    {500, "Internal Server Error"},
    {501, "Not Implemented"}
};

// SIGINT 信号处理函数
static void on_sigint(int sig) {
    (void)sig;
    g_stop = 1;  // 设置 g_stop 为 1 来停止服务器
}

// 去除字符串两边的空格
static char* trim_spaces(char* s) {
    char* end;
    // 去掉前面的空格
    while (*s && isspace((unsigned char)*s)) {
        s++;
    }
    if (*s == '\0') {
        return s;
    }
    // 去掉后面的空格
    end = s + strlen(s) - 1;
    while (end > s && isspace((unsigned char)*end)) {
        end--;
    }
    end[1] = '\0';
    return s;
}

// 忽略大小写的字符串比较函数
static int ascii_strncasecmp(const char* a, const char* b, size_t n) {
    size_t i;
    for (i = 0; i < n; ++i) {
        unsigned char ca = (unsigned char)a[i];
        unsigned char cb = (unsigned char)b[i];
        int diff = tolower(ca) - tolower(cb);
        if (diff != 0 || ca == '\0' || cb == '\0') {
            return diff;
        }
    }
    return 0;
}

// 查找 HTTP 请求头部结束的标记
static char* find_header_terminator(const char* buf, size_t len) {
    size_t i;
    if (len < 4) {
        return NULL;  // 长度小于4，无法构成有效的 HTTP 头部
    }
    // 遍历查找 "\r\n\r\n" 作为头部结束标志
    for (i = 0; i + 3 < len; ++i) {
        if (buf[i] == '\r' && buf[i + 1] == '\n'
            && buf[i + 2] == '\r' && buf[i + 3] == '\n') {
            return (char*)(buf + i);
        }
    }
    return NULL;
}

// 提取 HTTP 请求中的 Content-Length
static int extract_content_length(const char* buf, size_t header_len) {
    const char* cursor = buf;
    const char* end = buf + header_len;

    while (cursor + 2 <= end) {
        const char* line_end = NULL;
        const char* p;
        // 遍历每一行，找到 "\r\n"
        for (p = cursor; p + 1 <= end; ++p) {
            if (p[0] == '\r' && p[1] == '\n') {
                line_end = p;
                break;
            }
        }
        if (!line_end) {
            break;  // 如果没有找到行尾，则退出
        }
        size_t line_len = (size_t)(line_end - cursor);
        if (line_len == 0) {
            break;  // 空行，结束
        }
        if (line_len >= MAX_HEADER_LEN) {
            line_len = MAX_HEADER_LEN - 1;  // 防止超长行
        }

        char line[MAX_HEADER_LEN];
        memcpy(line, cursor, line_len);  // 复制当前行
        line[line_len] = '\0';  // 给行末加上终止符

        // 如果当前行是 Content-Length，则提取出它的值
        if (ascii_strncasecmp(line, "Content-Length:", 15) == 0) {
            const char* value = line + 15;
            while (*value && isspace((unsigned char)*value)) {
                value++;  // 跳过空格
            }
            return atoi(value);  // 返回 Content-Length 的值
        }

        cursor = line_end + 2;  // 移动到下一行
    }
    return -1;  // 未找到 Content-Length
}

// 发送数据函数，确保全部数据发送成功
static int send_all_data(int fd, const void* buf, size_t len) {
    const char* p = (const char*)buf;
    size_t left = len;

    while (left > 0) {
        ssize_t n = send(fd, p, left, 0);
        if (n < 0) {
            if (errno == EINTR) {
                continue;  // 被中断，继续尝试
            }
            return -1;  // 发送失败
        }
        if (n == 0) {
            return -1;  // 发送 0 字节，失败
        }
        p += n;  // 移动指针
        left -= (size_t)n;  // 剩余未发送字节数
    }
    return 0;
}

// 解析地址，获取 sockaddr_storage 地址结构
static int resolve_addr(const char* host, const char* port,
                        struct sockaddr_storage* out_addr, socklen_t* out_len) {
    struct addrinfo hints;
    struct addrinfo* res = NULL;
    int rc;

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;  // 只支持 IPv4
    hints.ai_socktype = SOCK_STREAM;  // 使用 TCP 协议
    hints.ai_flags = AI_PASSIVE | AI_NUMERICSERV;  // 被动模式，支持数字端口

    rc = getaddrinfo((host && host[0]) ? host : NULL, port, &hints, &res);
    if (rc != 0) {
        fprintf(stderr, "getaddrinfo failed: %s\n", gai_strerror(rc));
        return -1;
    }

    memcpy(out_addr, res->ai_addr, res->ai_addrlen);
    *out_len = (socklen_t)res->ai_addrlen;
    freeaddrinfo(res);
    return 0;
}

// 发送 HTTP 响应
static int send_http_response(int fd, int status_code,
                              const char* body, size_t body_len,
                              const char* extra_header) {
    const Status* statusInfo = NULL;
    size_t i;
    // 查找状态码对应的信息
    for (i = 0; i < sizeof(status_list) / sizeof(status_list[0]); ++i) {
        if (status_list[i].code == status_code) {
            statusInfo = &status_list[i];
            break;
        }
    }

    if (statusInfo == NULL) {
        return -1;  // 如果状态码无效，返回错误
    }

    char header[1024];
    // 构造 HTTP 响应头
    int header_len = snprintf(header, sizeof(header),
        "HTTP/1.1 %d %s\r\n"
        "Content-Length: %zu\r\n"
        "%s"
        "\r\n",
        statusInfo->code, statusInfo->msg,
        body_len, extra_header ? extra_header : "");

    if (header_len < 0 || (size_t)header_len >= sizeof(header)) {
        return -1;  // 如果头部过长或构造失败，返回错误
    }

    // 发送 HTTP 响应头
    if (send_all_data(fd, header, (size_t)header_len) != 0) {
        return -1;  // 发送头部失败
    }

    // 发送响应体
    if (body_len > 0 && body != NULL) {
        if (send_all_data(fd, body, body_len) != 0) {
            return -1;  // 发送 body 失败
        }
    }
    return 0;
}

// HTTP 请求结构体
typedef struct {
    char method[16];           // 请求方法 (GET, POST, PUT, DELETE)
    char uri[256];             // 请求的 URI
    char version[16];          // HTTP 版本
    char headers[MAX_HEADERS][MAX_HEADER_LEN];  // 请求头
    int num_headers;           // 请求头的数量
    char* body;                // 请求体
    size_t body_len;           // 请求体长度
    int content_length;        // 内容长度
} HttpRequest;

// 解析 HTTP 请求
static int parse_request(const char* buf, size_t buf_len, HttpRequest* request) {
    const char* p = buf;
    const char* end = buf + buf_len;
    int scan_result;

    memset(request, 0, sizeof(*request));
    request->content_length = -1;

    // 解析请求行
    scan_result = sscanf(p, "%15s %255s %15s",
                         request->method, request->uri, request->version);
    if (scan_result < 3) {
        return -1;  // 请求行格式不正确
    }
    if (strncmp(request->version, "HTTP/1.1", 8) != 0) {
        return -1;  // 不支持的 HTTP 版本
    }

    // 跳过请求行
    const char* start_line_end = strstr(p, "\r\n");
    if (!start_line_end) {
        return -1;  // 请求行格式错误
    }
    p = start_line_end + 2;

    // 解析请求头
    request->num_headers = 0;
    while (p < end && request->num_headers < MAX_HEADERS) {
        if (p + 2 <= end && strncmp(p, "\r\n", 2) == 0) {
            p += 2;  // 空行，结束请求头解析
            break;
        }

        char line[MAX_HEADER_LEN];
        char* colon;
        const char* next;

        if (sscanf(p, "%255[^\r\n]", line) < 1) {
            return -1;  // 解析请求头时出错
        }

        colon = strchr(line, ':');
        if (!colon) {
            return -1;  // 如果没有冒号，格式错误
        }

        *colon = '\0';
        {
            // 将请求头的键值对格式化
            char* key = trim_spaces(line);
            char* value = trim_spaces(colon + 1);
            snprintf(request->headers[request->num_headers],
                     MAX_HEADER_LEN, "%s: %s", key, value);
        }

        request->num_headers++;

        next = strstr(p, "\r\n");
        if (!next) {
            return -1;  // 请求头格式错误
        }
        p = next + 2;
    }

    // 查找 Content-Length 请求头
    for (int i = 0; i < request->num_headers; ++i) {
        if (ascii_strncasecmp(request->headers[i],
                              "Content-Length: ", 16) == 0) {
            request->content_length = atoi(request->headers[i] + 16);
            break;
        }
    }

    // 如果请求体存在，读取请求体
    if (request->content_length > 0) {
        size_t avail = (size_t)(end - p);
        if (avail < (size_t)request->content_length) {
            return -1;  // 请求体内容不完整
        }
        request->body = (char*)malloc((size_t)request->content_length + 1);
        if (!request->body) {
            return -1;  // 内存分配失败
        }
        memcpy(request->body, p, (size_t)request->content_length);
        request->body[request->content_length] = '\0';  // 添加终止符
        request->body_len = (size_t)request->content_length;
    }

    // 如果 URI 以 / 开头，去掉 /
    if (request->uri[0] == '/') {
        memmove(request->uri, request->uri + 1, strlen(request->uri));
    }

    return 0;
}

// 获取静态资源内容
static const char* get_static_resource(const char* path) {
    if (strcmp(path, "static/foo") == 0) return "Foo";
    if (strcmp(path, "static/bar") == 0) return "Bar";
    if (strcmp(path, "static/baz") == 0) return "Baz";
    return NULL;  // 如果没有匹配的路径，返回 NULL
}

// 动态资源结构体
typedef struct {
    char path[256];  // 资源路径
    char* content;   // 资源内容
    size_t content_len;  // 内容长度
} DynamicResource;

// 存储动态资源的数组
static DynamicResource dynamic_resources[MAX_RESOURCES];
static int num_dynamic = 0;

// 查找动态资源
static int find_dynamic(const char* path, DynamicResource** out_res) {
    int i;
    for (i = 0; i < num_dynamic; ++i) {
        if (strcmp(dynamic_resources[i].path, path) == 0) {
            *out_res = &dynamic_resources[i];
            return 1;
        }
    }
    return 0;
}

// 添加动态资源
static int add_dynamic(const char* path, const char* content, size_t len) {
    DynamicResource* r;
    if (num_dynamic >= MAX_RESOURCES) {
        return 0;  // 资源数已达上限，不能添加
    }

    r = &dynamic_resources[num_dynamic];
    strcpy(r->path, path);
    r->content = (char*)malloc(len + 1);
    if (!r->content) {
        return 0;  // 内存分配失败
    }
    memcpy(r->content, content, len);
    r->content[len] = '\0';
    r->content_len = len;
    num_dynamic++;
    return 1;
}

// 释放所有动态资源
static void free_dynamic(void) {
    int i;
    for (i = 0; i < num_dynamic; ++i) {
        free(dynamic_resources[i].content);
        dynamic_resources[i].content = NULL;
        dynamic_resources[i].content_len = 0;
    }
    num_dynamic = 0;
}

// 处理客户端请求
static int handle_request(int fd, const HttpRequest* request) {
    if (strcmp(request->method, "GET") != 0 &&
        strcmp(request->method, "PUT") != 0 &&
        strcmp(request->method, "DELETE") != 0) {
        return send_http_response(fd, 501, NULL, 0, NULL);  // 不支持的方法返回 501
    }

    // 处理静态资源
    if (strncmp(request->uri, "static/", 7) == 0) {
        if (strcmp(request->method, "GET") != 0) {
            return send_http_response(fd, 403, NULL, 0, NULL);  // 非 GET 方法禁止访问
        }
        {
            const char* s = get_static_resource(request->uri);
            if (s) {
                return send_http_response(fd, 200, s, strlen(s), NULL);  // 返回静态资源内容
            }
        }
        return send_http_response(fd, 404, NULL, 0, NULL);  // 未找到静态资源，返回 404
    }

    // 处理动态资源
    if (strncmp(request->uri, "dynamic/", 8) == 0) {
        DynamicResource* res = NULL;
        int exists = find_dynamic(request->uri, &res);

        if (strcmp(request->method, "GET") == 0) {
            if (exists) {
                return send_http_response(fd, 200,
                                          res->content, res->content_len, NULL);  // 返回动态资源
            }
            return send_http_response(fd, 404, NULL, 0, NULL);  // 未找到动态资源，返回 404
        }

        if (strcmp(request->method, "PUT") == 0) {
            if (!request->body) {
                return send_http_response(fd, 400, NULL, 0, NULL);  // 请求体为空，返回 400
            }
            if (exists) {
                char* new_buf = (char*)malloc(request->body_len + 1);
                if (!new_buf) {
                    return send_http_response(fd, 500, NULL, 0, NULL);  // 内存分配失败，返回 500
                }
                free(res->content);
                res->content = new_buf;
                memcpy(res->content, request->body, request->body_len);
                res->content[request->body_len] = '\0';
                res->content_len = request->body_len;
                return send_http_response(fd, 204, NULL, 0, NULL);  // 更新成功，返回 204
            }
            if (!add_dynamic(request->uri, request->body, request->body_len)) {
                return send_http_response(fd, 500, NULL, 0, NULL);  // 添加失败，返回 500
            }
            return send_http_response(fd, 201, NULL, 0, NULL);  // 创建成功，返回 201
        }

        if (strcmp(request->method, "DELETE") == 0) {
            if (exists) {
                free(res->content);
                if (res != &dynamic_resources[num_dynamic - 1]) {
                    *res = dynamic_resources[num_dynamic - 1];
                }
                num_dynamic--;
                return send_http_response(fd, 204, NULL, 0, NULL);  // 删除成功，返回 204
            }
            return send_http_response(fd, 404, NULL, 0, NULL);  // 未找到资源，返回 404
        }
    } else {
        if (strcmp(request->method, "GET") == 0) {
            return send_http_response(fd, 404, NULL, 0, NULL);  // 非动态/静态资源，返回 404
        }
        return send_http_response(fd, 403, NULL, 0, NULL);  // 禁止访问，返回 403
    }

    return send_http_response(fd, 500, NULL, 0, NULL);  // 发生错误，返回 500
}

// 处理接收到的缓冲区数据
static int process_buffer(int conn_fd, char* buffer,
                          size_t* buf_len, size_t buf_size) {
    while (*buf_len > 0) {
        char* header_end = find_header_terminator(buffer, *buf_len);
        if (!header_end) {
            break;  // 如果没有找到头部终止符，退出
        }

        size_t header_size = (size_t)(header_end - buffer) + 4;
        int content_length = extract_content_length(buffer, header_size);
        if (content_length < 0) {
            content_length = 0;  // 没有 Content-Length，默认为 0
        }

        size_t total_len = header_size + (size_t)content_length;
        if (total_len > buf_size) {
            send_http_response(conn_fd, 400, NULL, 0, NULL);  // 请求头过大，返回 400
            return -1;
        }
        if (*buf_len < total_len) {
            break;  // 缓冲区不足，继续等待数据
        }
        char temp_buf[RECV_BUF_SIZE + 1];
        memcpy(temp_buf, buffer, total_len);
        temp_buf[total_len] = '\0';

        {
            HttpRequest req;
            if (parse_request(temp_buf, total_len, &req) != 0) {
                send_http_response(conn_fd, 400, NULL, 0, NULL);  // 解析请求失败，返回 400
                free(req.body);
            } else {
                handle_request(conn_fd, &req);  // 处理请求
                free(req.body);
            }
        }
        memmove(buffer, buffer + total_len, *buf_len - total_len);
        *buf_len -= total_len;
    }
    return 0;
}

// 主程序入口
int main(int argc, char** argv) {
    const char* bind_ip;
    const char* port;
    struct sockaddr_storage addr;
    socklen_t addrlen = 0;
    int listen_fd;
    int yes = 1;
    char recv_buffer[RECV_BUF_SIZE];
    size_t buf_len = 0;

    if (argc != 3) {
        fprintf(stderr, "Usage: %s <bind_ip> <port>\n", argv[0]);
        return EXIT_FAILURE;  // 如果参数不正确，退出程序
    }

    signal(SIGINT, on_sigint);  // 监听 SIGINT 信号
    signal(SIGPIPE, SIG_IGN);  // 忽略 SIGPIPE 信号

    bind_ip = argv[1];
    port = argv[2];

    if (resolve_addr(bind_ip, port, &addr, &addrlen) != 0) {
        return EXIT_FAILURE;  // 地址解析失败，退出程序
    }

    listen_fd = socket(addr.ss_family, SOCK_STREAM, 0);  // 创建套接字
    if (listen_fd < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));  // 设置套接字选项

    if (bind(listen_fd, (struct sockaddr*)&addr, addrlen) < 0) {  // 绑定端口
        perror("bind");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    if (listen(listen_fd, BACKLOG) < 0) {  // 监听端口
        perror("listen");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    printf("Listening on %s:%s ... (Ctrl+C to stop)\n", bind_ip, port);

    while (!g_stop) {
        struct sockaddr_storage peer;
        socklen_t peerlen = sizeof(peer);
        int conn_fd = accept(listen_fd, (struct sockaddr*)&peer, &peerlen);  // 等待客户端连接
        if (conn_fd < 0) {
            if (errno == EINTR) {
                continue;  // 被中断，继续等待
            }
            perror("accept");
            break;
        }

        buf_len = 0;
        while (!g_stop) {
            ssize_t chunk = recv(conn_fd,
                                 recv_buffer + buf_len,
                                 RECV_BUF_SIZE - buf_len, 0);  // 接收客户端数据
            if (chunk == 0) {
                break;  // 客户端关闭连接
            }
            if (chunk < 0) {
                if (errno == EINTR) {
                    continue;  // 被中断，继续尝试
                }
                perror("recv");
                break;
            }

            buf_len += (size_t)chunk;

            if (process_buffer(conn_fd, recv_buffer, &buf_len, RECV_BUF_SIZE) != 0) {
                break;  // 数据处理出错，退出
            }

            if (buf_len == RECV_BUF_SIZE) {
                send_http_response(conn_fd, 400, NULL, 0, NULL);  // 缓冲区满，返回 400
                buf_len = 0;
            }
        }

        close(conn_fd);  // 关闭连接
    }

    close(listen_fd);  // 关闭监听套接字
    free_dynamic();  // 释放动态资源
    printf("Server stopped.\n");
    return EXIT_SUCCESS;  // 服务器停止
}
