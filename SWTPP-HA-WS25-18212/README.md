# SWTPP-HA-WS25-18212

这是一个用 Haskell 实现的 Martian Chess 作业项目。项目使用 Stack 管理构建、依赖和测试。

## 项目内容

核心模块：

- `src/Board.hs`：定义棋盘、棋子、玩家、位置，以及 FEN 校验和棋盘转换逻辑。
- `src/Logic.hs`：实现棋子移动规则、执行移动、计分和胜负判断。
- `app/Main.hs`：提供命令行入口，用于调用移动生成、执行移动和胜负判断等功能。
- `test/Spec.hs`：Hspec 单元测试。
- `validate/Spec.hs`：验证测试。

## 环境要求

- Stack
- GHC 由 Stack 根据 `stack.yaml` 自动管理

## 构建

```bash
stack build
```

清理构建产物：

```bash
stack clean
```

## 测试

运行全部测试：

```bash
stack test
```

运行单元测试：

```bash
stack test martian-chess:units
```

运行验证测试：

```bash
stack test martian-chess:validate
```

生成覆盖率报告：

```bash
stack test martian-chess:units --coverage
```

## 命令行用法

构建后可以通过 `stack exec` 调用程序：

```bash
stack exec martian-chess -- pawnMoves "<fen>" Bottom a1 ""
stack exec martian-chess -- droneMoves "<fen>" Top b6 "a5-a6"
stack exec martian-chess -- queenMoves "<fen>" Bottom d1 ""
stack exec martian-chess -- makeMove "<fen>" "a1-b2"
stack exec martian-chess -- playerWon "<fen>" Top 3 2
```

其中：

- `<fen>` 表示当前棋盘状态。
- 玩家参数为 `Top` 或 `Bottom`。
- 移动格式为 `起点-终点`，例如 `a1-b2`。

## 初始棋盘

项目中的标准初始 FEN：

```text
qqd1/qdp1/dpp1///1ppd/1pdq/1dqq
```
