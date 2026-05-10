#define _GNU_SOURCE // 启用 GNU 扩展, 以使用某些特定函数,如 getline, strcasestr 等来做字符串处理
#include <arpa/inet.h> // 提供了定义互联网操作的函数和结构，如套接字编程，IP 地址转换等
#include <ctype.h>    // 提供字符处理函数，如 isspace, isdigit 等，用于字符分类和转换
#include <errno.h>    // 定义了错误码变量 errno 和相关的错误码，用于错误处理，如 EINTR， EAGAIN 等
#include <netdb.h>    // 提供网络数据库操作的函数和结构，如 getaddrinfo, freeaddrinfo 等,用于域名解析,服务名解析等
#include <signal.h>   // 提供信号处理函数和结构，如 signal, sigaction 等，用于处理异步事件
#include <stdio.h>    // 提供输入输出函数，如 printf, perror 等，用于标准输入输出操作
#include <stdlib.h>   // 提供通用工具函数，如 malloc, free, atoi 等，用于内存管理和转换,程序退出等
#include <string.h>   // 提供字符串处理函数，如 strcmp, strcpy, strlen 等，用于字符串操作
#include <sys/socket.h> // 提供套接字编程的函数和结构，如 socket, bind, listen, accept 等，用于网络通信
#include <sys/types.h>  // 定义了一些基本数据类型，如 size_t, ssize_t 等，用于系统调用
#include <unistd.h>     // 提供对 POSIX 操作系统 API 的访问，如 read, write, close 等，用于文件和进程操作   

//宏定义：定义服务器的基本参数
//服务器储存最大资源数
#define fuwuqizuida_RESOURCES 100 // 最大动态资源数,防止内存溢出
//最大请求头长度
#define fuwuqizuida_HEADER_LEN 256 // 最大请求头长度,防止超长请求头攻击
//接收缓冲区大小
#define jieshou_huanchongBuffer_SIZE 8192 // 接收缓冲区大小,防止缓冲区溢出,提高性能,题目要求假设请求小于8192字节
//监听队列长度
#define L_BACKLOG 16 // 监听队列长度,防止拒绝服务攻击，提高并发处理能力，listen()时允许的最大等待连接数
//题目假设最多40个头部
#define fuwuqizuida_HEADERS 40 // 最大头部数,防止头部过多导致资源耗尽，提高安全性，提高性能，题目假设最多40个头部


//-------
//退出服务器的全局变量，用在while(!g_stop)循环中,配合SIGINT（Ctrl+C）信号使用
static volatile sig_atomic_t g_stop = 0; // 全局变量，用于标识是否收到停止信号，类型为 sig_atomic_t 保证在信号处理函数中安全访问
//static用于限制变量作用域在当前文件内，可用可不用，因为我们只有一个文件，volatile用于防止编译器优化，确保每次访问都从内存中读取最新值
//sig_atomic_t 是一种特殊的整数类型，保证对该类型变量的读写操作是原子的，在信号处理函数中使用可以避免竞态条件
//g_stop 用于在收到 SIGINT 信号时停止服务器运行,0表示继续运行,1表示停止运行


//-------
//aufgabe 2.4, 2.5-2.7
//http 状态码结构体
//为了表示 HTTP 响应状态码及其对应的描述信息，定义了 Status 结构体，包含两个成员：code 和 msg
typedef struct {
    int code;        // 状态码，如 200, 404 等
    const char* msg; // 状态描述，如 "OK", "Not Found" 等
} Status; // Status 结构体用于表示 HTTP 响应状态码及其描述信息，句尾Status为结构体类型名，必须再次声明



//http 状态码列表（部分常用状态码）
//用于发送 HTTP 响应时使用，描述响应的状态，如 200 OK, 404 Not Found 等
//要求生成的服务器需要返回部分状态码，如 200, 201, 204, 400, 403, 404, 500, 501
static const Status http_status_list[] = {
    {200, "OK"},
    {201, "Created"},
    {204, "No Content"},
    {400, "Bad Request"},
    {403, "Forbidden"},
    {404, "Not Found"},
    {500, "Internal Server Error"},
    {501, "Not Implemented"}
};

//先做信号处理
//-------
//ctrl+c 信号处理函数
//当收到 SIGINT 信号时调用此函数，设置 g_stop 为 1 来停止服务器
//能让我们更快速优雅的退出服务器程序
//非必须
static void on_sigint(int sig) {
    (void)sig; // 避免未使用参数的编译器警告
    g_stop =1; // 设置 g_stop 为 1 来停止服务器
}

//2.5-2.7的辅助代码
//trimmakespaces 函数用于去除字符串两端的空格
//用在http请求头解析中，确保头部字段和值没有多余的空格，提高解析准确性，防止因空格导致的错误，key/value对不上的问题
static char* trimmakespaces(char* s) {
    char* end;
    // 去掉前面的空格
    while (*s && isspace((unsigned char)*s)) { // 强制转换为 unsigned char 以避免负值问题
        s++;// 移动指针跳过空格,直到遇到非空格字符或字符串结束
    }
    if (*s == '\0') { // 如果字符串全是空格，返回空字符串,避免后续操作出错
        return s;// 返回指向字符串结束的指针
    }
    // 去掉后面的空格
    end = s + strlen(s) - 1; // 指向字符串的最后一个字符,准备去除末尾空格
    while (end > s && isspace((unsigned char)*end)) { // 强制转换为 unsigned char 以避免负值问题,防止死循环,确保 end 不越过 s
        end--; // 移动指针跳过空格,直到遇到非空格字符,或指针与 s 相遇,表示字符串中间没有非空格字符,--此时字符串全是空格
    }
    end[1] = '\0'; // 在第一个非空格字符后添加字符串终止符,截断字符串,完成去除末尾空格
    return s;// 返回指向去除前导空格后的字符串起始位置的指针,确保字符串两端无空格
}

//忽略大小写的字符串比较函数
//用于比较 HTTP 头部字段名时忽略大小写差异，提高兼容性，防止因大小写不同导致的匹配失败
static int bigsmallokay(const char* a, const char* b, size_t n) {
    size_t i;
    for (i = 0; i < n; ++i) { // 遍历前 n 个字符进行比较
        unsigned char ca = (unsigned char)a[i];// 强制转换为 unsigned char 以避免负值问题,ca为当前字符
        unsigned char cb = (unsigned char)b[i];// 强制转换为 unsigned char 以避免负值问题,cb为当前字符
        int diff = tolower(ca) - tolower(cb); // 转为小写进行比较
        if (diff != 0 || ca == '\0' || cb == '\0') { // 如果字符不同或遇到字符串结束
            return diff; // 返回差异值或在遇到字符串结束时返回
        }
    }
    return 0; // 前 n 个字符相等，返回 0
}   

//-------
//aufgabe 2.3
//pakete erkkennen
//查找 HTTP 请求头部结束的标记
//用于确定 HTTP 请求头部的结束位置，便于后续解析请求头和请求体
static char* find_header_endsignal(const char* buf, size_t len){
    size_t i;
    if (len < 4) {
        return NULL;  // 长度小于4，无法构成有效的 HTTP 头部
        //不可能包含 "\r\n\r\n"
    }
    // 遍历查找 "\r\n\r\n" 作为头部结束标志
    for (i = 0; i + 3 < len; ++i) {
        if (buf[i] == '\r' && buf[i + 1] == '\n'// 查找头部结束标志
            && buf[i + 2] == '\r' && buf[i + 3] == '\n') { // 找到头部结束标志，表示请求头结束，
            return (char*)(buf + i); // 返回指向头部结束标志位置的指针
        }
    }
    return NULL; // 未找到头部结束标志，返回 NULL
}

//2.3，2.5-2.7的辅助代码
//提取 HTTP 请求中的 Content-Length
//用于获取请求体的长度，便于正确读取请求体内容
static int get_content_length(const char* buf, size_t header_len) {
    const char* cursor = buf;// 指向当前处理位置的指针，cursor 用于遍历请求头
    const char* end = buf + header_len; // 指向请求头结束位置的指针,end 用于确定遍历范围,防止越界

    while (cursor + 2 <= end) { // 确保至少有两字节可读以查找行结束符
        const char* line_end = NULL; // 指向当前行结束位置的指针
        const char* p;
        // 遍历每一行，找到 "\r\n"
        for (p = cursor; p + 1 <= end; ++p) {
            if (p[0] == '\r' && p[1] == '\n') { // 找到行结束符
                line_end = p; // 记录行结束位置
                break; // 退出循环，处理当前行
            }
        }
        if (!line_end) {
            break; // 如果没有找到行尾，则退出
        }
        size_t line_len = (size_t)(line_end - cursor); // 计算当前行长度
        if (line_len == 0) {
            break; // 空行，结束
        }
        if (line_len >= fuwuqizuida_HEADER_LEN) {
            line_len = fuwuqizuida_HEADER_LEN - 1; // 防止超长行
        }
        char line[fuwuqizuida_HEADER_LEN];
        memcpy(line, cursor, line_len); // 复制当前行
        line[line_len] = '\0'; // 添加字符串终止符，确保 line 是一个合法字符串
        //判断是否是 Content-Length 头部，如果是则提取长度值
        if (bigsmallokay(line, "Content-Length: ", 15) == 0) { // 忽略大小写比较头部字段名,15是"Content-Length: "的长度，不是字符串长度
            const char* value = line + 15; // 指向长度值部分
            while (*value && isspace((unsigned char)*value)) {
                value++; // 跳过空格
            }

            return atoi(value); // 提取并返回 Content-Length 值
        }

        cursor = line_end + 2; // 移动到下一行的开始位置,跳过 "\r\n",继续处理下一行
    }
    return -1; // 未找到 Content-Length 头部，返回 -1
}

//-------
//2.2-2.7辅助代码
//确保把缓冲区的数据全部通过send()发送出去
//解决tcp中短写和eintr中断问题，tcp是流式协议，send()可能不会一次发送完所有数据，eintr信号中断也会导致发送中断
static int sendall_data(int fd, const void* buf, size_t len){ // fd是目标文件描述符，buf是要发送的数据缓冲区，len是数据长度
    const char* p = (const char*)buf; // 指向当前发送位置的指针
    size_t left_length = len; // 剩余未发送的数据长度

    while (left_length > 0) { // 循环直到所有数据发送完毕
        ssize_t sent = send(fd, p, left_length, 0); // 尝试发送剩余数据
        if (sent < 0) { // 发送出错
            if (errno == EINTR) {
                continue; // 如果是被信号中断，继续发送
            }
            return -1; // 其他错误，返回 -1
        }
        if (sent == 0) {
            return -1; // 发送 0 字节，表示连接关闭，返回 -1
        }
        p += (size_t)sent; // 移动指针到已发送数据后面
        left_length -= (size_t)sent; // 更新剩余未发送数据长度
    }
    return 0; // 全部数据发送成功，返回 0
}

//-------
//地址解析
//2.1 listen socket
static int resolve_address(const char* ip, const char* port,
                           struct sockaddr_storage* out_addr,
                           socklen_t* out_addrlen) {
    struct addrinfo hints; // 用于设置地址解析选项的结构体
    struct addrinfo* res = NULL; // 用于存储解析结果的链表头指针，初始化为 NULL，以防止野指针
    int rc;// 存储 getaddrinfo 的返回值

    memset(&hints, 0, sizeof(hints)); // 初始化 hints 结构体为 0
    hints.ai_family = AF_UNSPEC; // 支持 IPv4 和 IPv6
    hints.ai_socktype = SOCK_STREAM; // 使用 TCP 流式套接字
    hints.ai_flags = AI_PASSIVE| AI_NUMERICSERV; // 用于服务器端，自动填充本地地址,只接受数字端口,提高安全性,防止服务名解析带来的不确定性
    rc = getaddrinfo((ip && ip[0]) ? ip : NULL, port, &hints, &res); // 解析地址和端口
    if (rc != 0) {
        fprintf(stderr, "getaddrinfo failed: %s\n", gai_strerror(rc));// 输出错误信息
        return -1; // 解析失败，返回 -1
    }

    memcpy(out_addr, res->ai_addr, res->ai_addrlen); // 复制解析结果到输出参数
    *out_addrlen = (socklen_t)res->ai_addrlen; // 设置输出地址长度
    freeaddrinfo(res); // 释放解析结果链表
    return 0; // 解析成功，返回 0
}

//http响应构造与发送
//2.4 syntaktisch korrekte antworten
static int sendhttp_antworten(int fd, int status_code,
                             const void* body, size_t body_len,
                             const char* extra_header) {
    const Status* statusInfo = NULL; // 指向状态码信息的指针
    size_t i;

    // 查找对应的状态码信息
    for (i = 0; i < sizeof(http_status_list) / sizeof(http_status_list[0]); ++i) {
        if (http_status_list[i].code == status_code) {
            statusInfo = &http_status_list[i];
            break;
        }
    }
    if (!statusInfo) {
        return -1; // 未找到对应的状态码，返回错误
    }

    // 构造 HTTP 响应头
    char header[1024];
    int header_len = snprintf(header, sizeof(header),
        "HTTP/1.1 %d %s\r\n"
        "Content-Length: %zu\r\n"
        "%s"
        "\r\n",
        statusInfo->code, statusInfo->msg,
        body_len, extra_header ? extra_header : "");// 构造响应头，包含状态行和内容长度

    if (header_len < 0 || (size_t)header_len >= sizeof(header)) {
        return -1;  // 如果头部过长或构造失败，返回错误
    }

    // 发送 HTTP 响应头
    if (sendall_data(fd, header, (size_t)header_len) != 0) {
        return -1;  // 发送头部失败
    }

    // 发送响应体
    if (body_len > 0 && body != NULL) {
        if (sendall_data(fd, body, body_len) != 0) {
            return -1;  // 发送 body 失败
        }
    }
    return 0;
}

//http请求结构体
typedef struct {
    char method[16]; // 请求方法，如 GET, POST 等
    char uri[256];  // 请求的 URI, 如 /index.html,uri是统一资源标识符，用于标识请求的资源
    char version[16]; // HTTP 版本，如 HTTP/1.1
    // 题目假设最多40个头部
    char headers[fuwuqizuida_HEADERS][fuwuqizuida_HEADER_LEN]; // 存储请求头部
    int num_headers; // 请求头部数量
    char* body; // 请求体内容
    size_t body_len; // 请求体长度
    int content_length; // Content-Length 值
} HttpRequest;

//解析http请求
static int parse_http_request(const char* buf, size_t len, HttpRequest* request) {
    const char* end = buf + len; // 指向请求结束位置的指针
    const char* p = buf; // 指向当前处理位置的指针
    int i_scanned; // 用于存储 sscanf 的返回值

    memset(request,0,sizeof(*request)); // 初始化请求结构体为 0
    request->content_length = -1; // 初始化 Content-Length 为 -1，表示未设置
    // 解析请求行
    i_scanned = sscanf(p, "%15s %255s %15s", request->method,
                      request->uri, request->version);
    if (i_scanned < 3) {
        return -1; // 解析请求行失败，返回错误
    }

    //只接受http/1.1
    if (strncmp(request->version, "HTTP/1.1",8) != 0){
        return -1; // 不支持的 HTTP 版本，返回错误
    }

    //找到请求行结尾（\r\n），跳到headers部分开始
    const char* beginline_end = strstr(p, "\r\n");
    if (!beginline_end) {
        return -1; // 请求行格式错误，返回错误
    }
    p = beginline_end + 2; // 移动指针到请求头部开始位置
    // 解析请求头部
    request->num_headers = 0;
    while (p < end && request->num_headers < fuwuqizuida_HEADERS){ // 遍历请求头部，直到结束或达到最大头部数
        if (p+2<=end &&strncmp(p, "\r\n",2) == 0){
            p += 2; // 跳过空行
            break; // 遇到空行，结束请求头部解析
        }

        char line[fuwuqizuida_HEADER_LEN]; // 存储当前请求头行
        char* colon;    // 指向冒号位置的指针
        const char* next; // 指向下一行开始位置的指针,这里用const是为了防止修改原始数据，const char*更安全

        //读取一行（不包含\r\n）
        if(sscanf(p, "%255[^\r\n]", line) < 1) {
            return -1; // 解析请求头时出错
        }

        colon = strchr(line, ':'); // 查找冒号位置
        if (!colon) {
            return -1; // 请求头格式错误，返回错误
        }

        *colon = '\0'; // 将冒号替换为字符串终止符，分割键和值
        {
            // 去除键和值的空格，并格式化存储
            char* key = trimmakespaces(line); // 去除键的空格
            char* value = trimmakespaces(colon + 1); // 去除值的空格
            snprintf(request->headers[request->num_headers],
                     fuwuqizuida_HEADER_LEN, "%s: %s", key, value); // 格式化存储头部
        }
        request->num_headers++;
        // 移动指针到下一行开始位置
        next = strstr(p, "\r\n");
        if (!next) {
            return -1; // 请求头格式错误，返回错误
        }
        p = next + 2;// 跳过 "\r\n"，继续处理下一行
    }

    // 查找 Content-Length 请求头
    int i;
    for (i = 0; i < request->num_headers; ++i) {
        if (bigsmallokay(request->headers[i], "Content-Length: ", 16) == 0) {
            request->content_length = atoi(request->headers[i] + 16); // 提取 Content-Length 值
            break;
        }
    }

    // 如果请求体存在，读取请求体
    if (request->content_length > 0) {
        size_t avail = (size_t)(end - p);// 可用数据长度
        if (avail < (size_t)request->content_length) {
            return -1; // 请求体内容不完整
        }
        request->body = (char*)malloc((size_t)request->content_length + 1); // 分配内存存储请求体
        if (!request->body) {
            return -1;  // 内存分配失败
        }
        memcpy(request->body, p, (size_t)request->content_length); // 复制请求体内容
        request->body[request->content_length] = '\0'; // 添加字符串终止符，方便后续处理，避免字符串操作越界
        request->body_len = (size_t)request->content_length; // 设置请求体长度，方便后续处理，如 PUT 请求，读取请求体内容，如保存动态资源，避免多次计算长度，提高性能， 便于管理
    }

    //统一把uri前面的/去掉，方便后续处理
    //这样内部就可以写成 static/foo 而不是 /static/foo
    if (request->uri[0] == '/') {
        memmove(request->uri, request->uri + 1, strlen(request->uri));
    }

    return 0; // 解析成功，返回 0
}

//静态资源处理
//2.6 Statischer Inhalt
//get_static_resource 函数用于获取静态资源内容
// 题目要求：
//   static/foo -> "Foo"
//   static/bar -> "Bar"
//   static/baz -> "Baz"
// 未命中的返回 NULL，让上层用 404 Not Found 回复。
static const char* get_static_resource(const char* path) {
    if (strcmp(path, "static/foo") == 0) return "Foo"; 
    if (strcmp(path, "static/bar") == 0) return "Bar";
    if (strcmp(path, "static/baz") == 0) return "Baz";
    return NULL;  // 如果没有匹配的路径，返回 NULL
}

//动态资源处理
//2.7 Dynamischer Inhalt
//动态资源结构体
//用于存储动态资源的信息，包括路径、内容和内容长度
//DynaremicContent 结构体用于表示动态资源，包含路径、内容和内容长度
typedef struct {
    char path[256]; // 资源路径
    char* content; // 资源内容
    size_t content_len; // 内容长度,和之前的body_len，content_length区分开，避免混淆,body_len是请求体长度，content_length是请求体的Content-Length头部值,content_len是动态资源内容长度
} DynamicContent; // DynamicContent 结构体用于表示动态资源，包含路径、内容和内容长度,也可以叫做 DynamicResource

// 存储动态资源的数组
static DynamicContent dynamic_contents[fuwuqizuida_RESOURCES];
static int num_dynamic = 0; // 当前动态资源数量,初始为 0,方便后续添加和管理动态资源,防止越界,用于添加新资源时检查是否超过最大数量,已经添加的动态资源数量

// 查找动态资源
//用于根据路径查找动态资源，返回是否找到以及资源指针
// find_dynamicContent: 在动态资源数组中查找给定 path。
//   - 找到：*out_res 指向该资源，返回 1
//   - 未找到：返回 0
// 支持 GET/PUT/DELETE 对 dynamic/... 的操作。
static int find_dynamicContent(const char* path, DynamicContent** out_res) { // path 是要查找的资源路径，out_res 是输出参数，指向找到的资源指针
    int i;// 循环变量
    for (i = 0; i < num_dynamic; ++i) { // 遍历动态资源数组,查找匹配的路径,直到找到或遍历完所有资源
        if (strcmp(dynamic_contents[i].path, path) == 0) {// 找到匹配的路径
            *out_res = &dynamic_contents[i];// 设置输出参数为找到的资源指针，方便调用者访问该资源，避免多次查找，提高效率
            return 1; // 找到资源，返回 1
        }
    }
    return 0; // 未找到资源，返回 0
}

//动态资源的创建添加
//add_dynamicContent: 添加新的动态资源到数组中,新建一条dynamic/...资源，保存path->content映射
//题目要求：PUT dynamic/... 在不存在时创建新资源（返回 201 Created）
static int add_dynamicContent(const char* path, const char* content, size_t len) {
    DynamicContent* r; // 指向新资源的指针
    if (num_dynamic >= fuwuqizuida_RESOURCES) {
        return 0;  // 资源数已达上限，不能添加
    }   
    r = &dynamic_contents[num_dynamic]; // 获取下一个可用的资源位置，准备添加新资源
    strcpy(r->path, path); // 复制资源路径
    r->content = (char*)malloc(len + 1); // 分配内存存储资源内容
    if (!r->content) {
        return 0;  // 内存分配失败
    }
    memcpy(r->content, content, len); // 复制资源内容
    r->content[len] = '\0'; // 添加字符串终止符，确保内容是合法字符串
    r->content_len = len; // 设置内容长度
    num_dynamic++; // 增加动态资源数量
    return 1; // 添加成功，返回 1
}

//2.7的辅助代码
//释放所有动态资源，在服务器关闭时调用，防止内存泄漏
static void free_dynamicContent(void) {
    int i;
    for (i = 0; i < num_dynamic; ++i) {
        free(dynamic_contents[i].content); // 释放资源内容内存
        dynamic_contents[i].content = NULL; // 设置指针为 NULL，防止悬空指针
        dynamic_contents[i].content_len = 0; // 重置内容长度
    }
    num_dynamic = 0; // 重置动态资源数量
}

//请求处理函数
//2.5 semantisch korrekte antworten(400/404/403/501)
//2.6 Statischer Inhalt unter static/
//2.7 Dynamischer Inhalt unter dynamic/
//handle_anfrage 函数用于处理客户端请求:根据解析好的 HttpRequest 结构体，处理静态和动态资源请求，并发送相应的 HTTP 响应
//要求生成的服务器需要正确处理静态资源请求和动态资源的 CRUD 操作
//不支持的方法返回 501 Not Implemented
//static/... 的 GET 请求返回对应静态内容，未命中返回 404 Not Found,存在返回 200 OK
//dynamic/... 支持 GET/PUT/DELETE 方法的动态资源操作，按题目要求返回相应状态码
//其他路径的 GET 请求返回 404 Not Found，其他方法返回 403 Forbidden
static int handle_anfrage(int fd, const HttpRequest* request) {
    if (strcmp(request->method, "GET") != 0 &&
        strcmp(request->method, "PUT") != 0 &&
        strcmp(request->method, "DELETE") != 0) {
        return sendhttp_antworten(fd, 501,NULL, 0, NULL);  // 不支持的方法返回 501
    }

    // 处理静态资源
    if (strncmp(request->uri, "static/", 7) == 0) { // 处理 static/ 路径的请求,7是"static/"的长度
        if (strcmp(request->method, "GET") != 0) { //strcmp返回0表示相等,否则不等,非 GET 方法禁止访问，返回 403
            return sendhttp_antworten(fd, 403,
                                      NULL, 0, NULL);  // 非 GET 方法禁止访问，返回 403
        }
        const char* res = get_static_resource(request->uri);
        if (res) {
            return sendhttp_antworten(fd, 200,res, strlen(res), NULL);  // 返回静态资源，返回 200
        }
        return sendhttp_antworten(fd, 404,NULL, 0, NULL);  // 未找到静态资源，返回 404
    }

    // 处理动态资源
    if (strncmp(request->uri, "dynamic/", 8) == 0) { // 处理 dynamic/ 路径的请求,8是"dynamic/"的长度
        DynamicContent* res = NULL;
        int exists = find_dynamicContent(request->uri, &res);

        if (strcmp(request->method, "GET") == 0) { // GET 方法用于获取动态资源, 0 表示不存在，1 表示存在
            if (exists) {
                return sendhttp_antworten(fd, 200,res->content, res->content_len, NULL);  // 返回动态资源
            }
            return sendhttp_antworten(fd, 404, NULL, 0, NULL);  // 未找到动态资源，返回 404
        }

        if (strcmp(request->method, "PUT") == 0) { // PUT 方法用于创建或更新动态资源, 0 表示不存在，1 表示存在
            if (!request->body) {
                return sendhttp_antworten(fd, 400,NULL, 0, NULL);  // 请求体为空，返回 400
            }
            if (exists) {
                char* new_buf = (char*)malloc(request->body_len + 1);
                if (!new_buf) {
                    return sendhttp_antworten(fd, 500,NULL, 0, NULL);  // 内存分配失败，返回 500
                }
                free(res->content); // 释放旧内容内存
                res->content = new_buf; // 更新内容指针,指向新内存,避免内存泄漏
                memcpy(res->content, request->body, request->body_len); // 复制新内容
                res->content[request->body_len] = '\0'; // 添加字符串终止符
                res->content_len = request->body_len; // 更新内容长度
                return sendhttp_antworten(fd, 200,NULL, 0, NULL);  // 已存在资源，更新内容，返回 200 OK
            }
            if (add_dynamicContent(request->uri, request->body, request->body_len)) {// 添加新资源
                return sendhttp_antworten(fd, 201,NULL, 0, NULL);  // 新建资源，返回 201 Created
            }
            return sendhttp_antworten(fd, 500,NULL, 0, NULL);
        }

        // DELETE 方法用于删除动态资源
        if (strcmp(request->method, "DELETE") == 0) {
            if (exists) { //删除这个条目是为了保持数组的连续性，用尾元覆盖
                free(res->content);// 释放资源内容内存
                if(res != &dynamic_contents[num_dynamic - 1]) {
                    *res = dynamic_contents[num_dynamic - 1]; // 用最后一个资源覆盖被删除的资源
                }
                num_dynamic--; // 减少动态资源数量
                return sendhttp_antworten(fd, 204,NULL, 0, NULL);// 删除成功，返回 204 No Content
            }
            return sendhttp_antworten(fd, 404,NULL, 0, NULL);  // 未找到资源，返回 404
        }
    }else {
        // 其他路径的请求
        if (strcmp(request->method, "GET") == 0) {
            return sendhttp_antworten(fd, 404,NULL, 0, NULL);  // 未找到资源，返回 404
        }
        return sendhttp_antworten(fd, 403,NULL, 0, NULL);  // 非 GET 方法禁止访问，返回 403
    }
    //理论不会发生的兜底500
    return sendhttp_antworten(fd, 500,NULL, 0, NULL);
}

//处理接收缓冲区数据，http分包，分包是指tcp流式协议中，数据可能被拆分成多次接收，以解决粘包和半包问题，粘包是指多个请求被合并在一起，半包是指一个请求被拆分成多次接收，半包是最常见的情况，常见于大请求体，发生在 recv() 时，需要在应用层处理，确保每个请求都能被完整接收和处理
//2.3 Pakete erkkennen
//2.5-2.7 结合parse_http_request和handle_anfrage处理完整请求
//prozess_receive_buffer 函数用于处理接收缓冲区的数据，解析完整的 HTTP 请求并调用请求处理函数
//1.使用 find_header_endsignal 查找请求头部结束标志
//2.使用get_content_length 获取请求体长度
//3.调用 parse_http_request 解析请求，成功后调用 handle_anfrage 处理请求
//4.把处理完的请求从缓冲区移除，保留未处理的数据
static int prozess_receive_buffer(int fd, char* buf, size_t* buf_len, size_t max_buf_size) {
    while(*buf_len > 0) {
        char* header_end = find_header_endsignal(buf, *buf_len); // 查找请求头部结束标志
        if (!header_end) {
            break; // 未找到完整请求头，等待更多数据
        }

        size_t header_len = (size_t)(header_end - buf) + 4; // 计算请求头长度，包括 "\r\n\r\n"
        int content_length = get_content_length(buf, header_len); // 获取 Content-Length 值
        if (content_length < 0) {
            content_length = 0; // 如果未找到 Content-Length，默认为 0
        }
        size_t total_request_len = header_len + (size_t)content_length; // 计算完整请求长度
        if (*buf_len < total_request_len) {
            break; // 请求体不完整，等待更多数据
        }

        if(total_request_len > max_buf_size) {
            return -1; // 请求过大，返回错误
        }
        char temporary_buf[jieshou_huanchongBuffer_SIZE + 1]; // 临时缓冲区存储完整请求,+1是为了添加字符串终止符,防止字符串操作越界
        memcpy(temporary_buf, buf, total_request_len); // 复制完整请求到临时缓冲区,memcpy不会添加字符串终止符，需要手动添加,防止字符串操作越界
        temporary_buf[total_request_len] = '\0'; // 添加字符串终止符，确保临时缓冲区是合法字符串

        {
            HttpRequest request; // 存储解析后的请求
            if (parse_http_request(temporary_buf, total_request_len, &request) != 0) {
                sendhttp_antworten(fd, 400,NULL, 0, NULL);  // 解析请求失败，返回 400
                free(request.body); // 释放请求体内存
            }
            else {
                handle_anfrage(fd, &request); // 处理请求
                free(request.body); // 释放请求体内存
            }
        }
        //把剩余未处理的数据移动到缓冲区开头
        memmove(buf, buf + total_request_len, *buf_len - total_request_len);
        *buf_len -= total_request_len; // 更新缓冲区长度
    }
    return 0; // 处理成功，返回 0
}

//main服务器主程序
//2.1 listen socket: 创建监听套接字，绑定地址，监听端口,socket/bind/listen + So_REUSEADDR用于快速重启服务器，避免地址占用错误
//2.2 anfragen beantworten: 接受客户端连接，接收请求数据，发送响应数据,accept/recv/send,接受tcp连接，处理请求
//2.3 Pakete erkkennen: 处理 TCP 流式协议中的粘包和半包问题，确保每个请求都能被完整接收和处理，把收来的tcp数据放到缓冲区，调用 prozess_receive_buffer 处理
//2.4-2.7 间接调用 sendhttp_antworten,parse_http_request,handle_anfrage,get_static_resource 等函数处理请求和发送响应

//main 函数是服务器程序的入口，负责初始化服务器，处理客户端连接和请求
//1.参数解析: 解析命令行参数，获取监听的 IP 地址和端口号 - ./webserver <bind_ip> <port>
//2.使用resolve_address 解析地址，创建监听套接字，绑定地址，监听端口
//3.创建监听socket，并设置 SO_REUSEADDR 选项，允许快速重启服务器
//4.主循环: 使用 accept 接受客户端连接，接收请求数据，调用 prozess_receive_buffer 处理请求，发送响应数据
//5.退出前关闭socket，释放动态资源内存，优雅退出
int main(int argc, char* argv[]) {
    const char* bind_ip;// 监听的 IP 地址
    const char* port;// 监听的端口号
    struct sockaddr_storage listen_addr;// 监听地址结构
    socklen_t listen_addrlen;// 监听地址长度
    int listen_fd;// 监听套接字文件描述符
    int yes = 1; // 用于设置套接字选项
    char receive_buffer[jieshou_huanchongBuffer_SIZE]; // 接收缓冲区
    size_t receive_buffer_len = 0; // 接收缓冲区长度

    // 解析命令行参数
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <bind_ip> <port>\n", argv[0]);
        return EXIT_FAILURE; // 参数错误，退出
    }

    signal(SIGINT, on_sigint); // 注册 SIGINT 信号处理函数，优雅退出服务器
    signal(SIGPIPE, SIG_IGN); // 忽略 SIGPIPE 信号，防止写入关闭的 socket 导致程序终止
    bind_ip = argv[1]; // 获取绑定的 IP 地址
    port = argv[2]; // 获取绑定的端口号
    // 解析监听地址
    if (resolve_address(bind_ip, port, &listen_addr, &listen_addrlen) != 0) {
        return EXIT_FAILURE; // 地址解析失败，退出
    }
    // 创建监听套接字
    listen_fd = socket(listen_addr.ss_family, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("socket failed");
        return EXIT_FAILURE; // 创建套接字失败，退出
    }
    // 设置套接字选项，允许地址重用
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    // 绑定地址到套接字
    if (bind(listen_fd, (struct sockaddr*)&listen_addr, listen_addrlen)< 0) {
        perror("bind failed");
        close(listen_fd);
        return EXIT_FAILURE; // 绑定地址失败，退出
    }
    // 监听端口
    if (listen(listen_fd, fuwuqizuida_RESOURCES) < 0) {
        perror("listen failed");
        close(listen_fd);
        return EXIT_FAILURE; // 监听失败，退出
    }
    printf("Server listening on %s:%s\n", bind_ip, port);
    // 主循环，接受和处理客户端连接
    while(!g_stop){
        struct sockaddr_storage client_addr; // 客户端地址结构
        socklen_t client_addrlen = sizeof(client_addr); // 客户端地址长度
        int client_fd;// 客户端套接字文件描述符

        // 接受客户端连接
        client_fd = accept(listen_fd, (struct sockaddr*)&client_addr, &client_addrlen);
        if (client_fd < 0) {
            if (errno == EINTR) {
                continue; // 被信号中断，继续接受连接
            }
            perror("accept failed");
            break; // 接受连接失败，退出循环
        }

        // 接收和处理客户端请求
        receive_buffer_len = 0; // 重置接收缓冲区长度
        while (!g_stop) {
            ssize_t received = recv(client_fd, receive_buffer + receive_buffer_len,jieshou_huanchongBuffer_SIZE - receive_buffer_len, 0);
            if (received < 0) {
                if (errno == EINTR) {
                    continue; // 被信号中断，继续接收数据
                }
                perror("recv failed");
                break; // 接收数据失败，退出循环
            }
            if (received == 0) {
                break; // 客户端关闭连接，退出循环
            }
            receive_buffer_len += (size_t)received; // 更新接收缓冲区长度

            // 处理接收缓冲区的数据
            if (prozess_receive_buffer(client_fd, receive_buffer, &receive_buffer_len,
                                       jieshou_huanchongBuffer_SIZE) != 0) {
                break; // 处理数据失败，退出循环
            }
            if(receive_buffer_len == jieshou_huanchongBuffer_SIZE) {
                sendhttp_antworten(client_fd, 400,NULL, 0, NULL); // 缓冲区满，返回 400
                receive_buffer_len = 0; // 重置缓冲区长度
            }
        }

        close(client_fd); // 关闭客户端连接
    }

    close(listen_fd); // 关闭监听套接字
    free_dynamicContent(); // 释放动态资源内存
    printf("Server exiting  yeahyeah.\n");
    return EXIT_SUCCESS; // 正常退出
}