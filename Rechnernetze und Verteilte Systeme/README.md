# Rechnernetze und Verteilte Systeme

这个目录保存 Rechnernetze und Verteilte Systeme 课程的实践作业材料和代码，按 Praxis 1、Praxis 2、Praxis 3 分组。目录中同时包含题目 PDF、skeleton 压缩包、源码、测试脚本和部分本地构建产物。

## 目录结构

| 目录 | 内容 |
| --- | --- |
| `Praxis 1 Aufgabe-20251125/` | Praxis 1 的 HTTP/TCP webserver 练习。包含多个版本目录，例如 `praxis1/`、`praxis1 2/` 和 `praxis1 copy/`。主要源码是 `server.c`。 |
| `Praxis 2 Aufgabe-20260104/` | Praxis 2 的 HTTP webserver 和 DHT/Chord 相关练习。包含 `praxis2/`、`praxis2-v1/` 和 `praxis2-v2/` 多个版本。主要源码包括 `webserver.c`、`http.c`、`data.c`、`util.c` 以及对应头文件。 |
| `Praxis 3 Aufgabe-20260121/` | Praxis 3 的 ZeroMQ 分布式任务练习材料。包含 `praxis3/` skeleton、调试说明 PDF 和 VS Code 调试配置。 |

## 各 Praxis 说明

### Praxis 1

Praxis 1 主要实现一个基础 TCP/HTTP webserver。代码中包含 socket 初始化、请求接收、HTTP 请求解析、静态或动态资源处理以及响应发送逻辑。`CMakeLists.txt` 会生成名为 `webserver` 的可执行文件。

常用文件：

- `server.c`: webserver 主实现。
- `CMakeLists.txt`: CMake 构建配置。
- `requirements.txt`: Python 测试依赖。
- `test/check_submission.sh`: 打包、构建并运行 pytest 的检查脚本。

### Praxis 2

Praxis 2 在 HTTP webserver 基础上加入资源表和 DHT 逻辑。`webserver.c` 中包含节点信息、前驱/后继、UDP DHT 消息、hash 判断和请求重定向等逻辑。

常用文件：

- `webserver.c`: webserver 和 DHT 主要逻辑。
- `http.c` / `http.h`: HTTP 请求解析。
- `data.c` / `data.h`: 资源表的 get/set/delete 操作。
- `util.c` / `util.h`: 连接状态和通用工具。
- `test/`: pytest 测试和 DHT 测试辅助代码。

### Praxis 3

Praxis 3 目录目前主要是 skeleton 和调试材料。`CMakeLists.txt` 里预留了 `zmq_distributor` 和 `zmq_worker` 两个目标，需要把 `<source files>` 替换成实际源文件后才能完整构建。

## 构建与测试

每个 Praxis 子目录通常都带有自己的 `CMakeLists.txt` 和 `test/check_submission.sh`。进入具体版本目录后可以运行：

```bash
cmake -B build
cmake --build build
```

如果要按课程测试脚本打包并运行 pytest：

```bash
./test/check_submission.sh praxis1
./test/check_submission.sh praxis2
./test/check_submission.sh praxis3
```

实际参数要和当前目录对应，例如在 Praxis 2 的目录中运行 `praxis2`，在 Praxis 3 的目录中运行 `praxis3`。

## 备注

仓库中包含了一些本地构建产物，例如 `build/`、可执行文件、`__pycache__/` 和 skeleton 压缩包。这些文件可以帮助还原当时的工作状态，但如果要长期维护，建议后续用 `.gitignore` 排除自动生成内容，只保留源码、测试和说明文档。
