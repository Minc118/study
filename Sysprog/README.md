# Sysprog

## English

This directory contains C source files for a system programming exercise about CPU scheduling. The code is split by scheduling strategy, and `scheduler.c` acts as the central entry point that calls the selected algorithm based on the given `scheduling_strategy`.

### Contents

| File | Description |
| --- | --- |
| `scheduler.c` | Main scheduler flow: initializes processes, advances time, handles newly arriving processes, calls the selected scheduling algorithm, and records the resulting schedule. |
| `FCFS.c` | Example implementation of First Come First Served scheduling. |
| `PRIONP.c` | Framework for non-preemptive priority scheduling. |
| `HRRN.c` | Framework for Highest Response Ratio Next scheduling. |
| `LCFSPR.c` | Framework for Last Come First Served Preemptive Resume scheduling. |
| `SRTN.c` | Framework for Shortest Remaining Time Next scheduling. |
| `RR.c` | Framework for Round Robin scheduling; the startup function receives the quantum. |
| `MLF.c` | Framework for Multi-Level Feedback Queue scheduling. |
| `queue.c` | Shared queue implementation used by the scheduling algorithms. |
| `colors.c` | Helper functions for colored terminal output. |

### Current Status

`scheduler.c` already connects all strategies to the common execution flow, and `FCFS.c` contains a basic example implementation. The other scheduling algorithms and `queue.c` still contain `TODO` placeholders, so the queue operations and strategy-specific logic need to be completed.

### Dependencies

These source files include headers from `../lib/*.h`, such as `queue.h`, `process.h`, `scheduler.h`, and the headers for each scheduling algorithm. This directory is therefore not a standalone C project by itself. It needs to be used together with the original exercise framework, including the `lib/` directory and a test driver or main program.

### Usage

In the complete course project structure, the files can typically be compiled and tested from the project root:

```bash
# Example: compile from a project root that contains lib/, a test driver, and Sysprog/
gcc -std=c11 -Wall -Wextra -Wpedantic Sysprog/*.c <other source files> -o scheduler
```

If only this directory is downloaded, the original framework headers and test driver must be added before the code can be compiled.

## 中文

这个目录保存系统编程练习中的 CPU 调度器相关 C 源码。代码按调度策略拆分成多个模块，由 `scheduler.c` 作为统一入口，根据传入的 `scheduling_strategy` 调用对应算法。

### 内容概览

| 文件 | 作用 |
| --- | --- |
| `scheduler.c` | 调度器主流程：初始化进程、按时间推进、处理新到达进程、调用选中的调度算法并记录最终调度结果。 |
| `FCFS.c` | First Come First Served 调度算法的示例实现。 |
| `PRIONP.c` | 非抢占式优先级调度框架。 |
| `HRRN.c` | Highest Response Ratio Next 调度框架。 |
| `LCFSPR.c` | Last Come First Served Preemptive Resume 调度框架。 |
| `SRTN.c` | Shortest Remaining Time Next 调度框架。 |
| `RR.c` | Round Robin 调度框架，启动函数接收 quantum。 |
| `MLF.c` | Multi-Level Feedback Queue 调度框架。 |
| `queue.c` | 调度算法共用的队列实现位置。 |
| `colors.c` | 终端彩色输出辅助函数。 |

### 当前状态

`scheduler.c` 已经把所有策略接入统一执行流程，`FCFS.c` 作为示例算法已经有基本逻辑。其余调度算法和 `queue.c` 里还保留了 `TODO` 占位，需要继续补全队列操作和具体策略逻辑。

### 依赖说明

这些源码引用了 `../lib/*.h` 里的头文件，例如 `queue.h`、`process.h`、`scheduler.h` 和各个算法头文件。因此这个目录本身不是一个完整的独立 C 项目，需要和原始练习框架中的 `lib/`、测试入口或主程序一起使用。

### 使用方式

通常做法是在课程提供的完整项目结构中，从项目根目录编译和测试：

```bash
# 示例：在包含 lib/、测试入口和 Sysprog/ 的项目根目录下编译
gcc -std=c11 -Wall -Wextra -Wpedantic Sysprog/*.c <其他源文件> -o scheduler
```

如果只下载了当前目录，需要先补齐原始练习框架中的头文件和测试驱动，才能进行编译。
