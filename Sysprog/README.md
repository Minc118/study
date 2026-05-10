# Sysprog

这个目录保存系统编程练习中的 CPU 调度器相关 C 源码。代码按调度策略拆分成多个模块，由 `scheduler.c` 作为统一入口，根据传入的 `scheduling_strategy` 调用对应算法。

## 内容概览

| 文件 | 作用 |
| --- | --- |
| `scheduler.c` | 调度器主流程：初始化进程、按时间推进、处理新到达进程、调用具体调度算法并输出调度结果。 |
| `FCFS.c` | First Come First Served 示例实现。 |
| `PRIONP.c` | 非抢占式优先级调度框架。 |
| `HRRN.c` | Highest Response Ratio Next 调度框架。 |
| `LCFSPR.c` | Last Come First Served Preemptive Resume 调度框架。 |
| `SRTN.c` | Shortest Remaining Time Next 调度框架。 |
| `RR.c` | Round Robin 调度框架，入口函数接收 quantum。 |
| `MLF.c` | Multi-Level Feedback Queue 调度框架。 |
| `queue.c` | 调度算法共用的队列接口实现位置。 |
| `colors.c` | 终端彩色输出辅助函数。 |

## 当前状态

`scheduler.c` 已经把所有策略接入统一执行流程，`FCFS.c` 作为示例算法已经有基本逻辑。其余调度算法和 `queue.c` 里还保留了 `TODO` 占位，需要继续补全队列操作和具体策略逻辑。

## 依赖说明

这些源码引用了 `../lib/*.h` 里的头文件，例如 `queue.h`、`process.h`、`scheduler.h` 和各个算法头文件。因此这个目录本身不是一个完整的独立 C 项目，需要和原始练习框架中的 `lib/`、测试入口或主程序一起使用。

## 使用方式

通常做法是在课程提供的完整项目结构中编译和测试：

```bash
# 示例：在包含 lib/、测试入口和 Sysprog/ 的项目根目录下编译
gcc -std=c11 -Wall -Wextra -Wpedantic Sysprog/*.c <其他源文件> -o scheduler
```

如果只下载了当前目录，需要先补齐练习框架中的头文件和测试驱动，才能进行编译。
