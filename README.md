# Study

这个仓库用于整理学习过程中的课程代码、作业项目和实验实现。

## 目录结构

| 目录 | 内容 |
| --- | --- |
| `Rechnernetze und Verteilte Systeme/` | 计算机网络与分布式系统相关内容 |
| `Sysprog/` | 系统编程相关代码，包括调度算法实现 |
| `SWTPP-HA-WS25-18212/` | Haskell 实现的 Martian Chess 作业项目 |

## SWTPP-HA-WS25-18212

`SWTPP-HA-WS25-18212` 是一个基于 Stack 的 Haskell 项目，核心内容是 Martian Chess 的棋盘表示和规则逻辑。

主要功能：

- FEN 字符串校验、棋盘构建和棋盘反序列化
- Pawn、Drone、Queen 三类棋子的合法移动计算
- 移动执行、吃子计分和胜负判断
- 命令行入口与 Hspec 单元测试、验证测试

常用命令：

```bash
cd SWTPP-HA-WS25-18212
stack build
stack test
stack test martian-chess:units
stack test martian-chess:validate
```

## 说明

仓库中的不同目录对应不同课程或实验内容，彼此相对独立。进入具体项目目录后，可以查看该目录下的 README、配置文件和测试文件了解运行方式。
