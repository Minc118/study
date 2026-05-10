# SWTPP-HA-WS25-18212

## English

This is a Haskell implementation of the Martian Chess assignment. The project uses Stack to manage builds, dependencies, and tests.

### Project Contents

Core modules:

- `src/Board.hs`: Defines the board, cells, players, positions, FEN validation, and conversion between FEN strings and board values.
- `src/Logic.hs`: Implements movement rules, move execution, scoring, and winner detection.
- `app/Main.hs`: Provides a command-line entry point for move generation, move execution, and winner detection.
- `test/Spec.hs`: Hspec unit tests.
- `validate/Spec.hs`: Validation tests.

### Requirements

- Stack
- GHC is managed by Stack according to `stack.yaml`.

### Build

```bash
stack build
```

Clean build artifacts:

```bash
stack clean
```

### Tests

Run all tests:

```bash
stack test
```

Run unit tests:

```bash
stack test martian-chess:units
```

Run validation tests:

```bash
stack test martian-chess:validate
```

Generate a coverage report:

```bash
stack test martian-chess:units --coverage
```

### Command-Line Usage

After building the project, the executable can be called with `stack exec`:

```bash
stack exec martian-chess -- pawnMoves "<fen>" Bottom a1 ""
stack exec martian-chess -- droneMoves "<fen>" Top b6 "a5-a6"
stack exec martian-chess -- queenMoves "<fen>" Bottom d1 ""
stack exec martian-chess -- makeMove "<fen>" "a1-b2"
stack exec martian-chess -- playerWon "<fen>" Top 3 2
```

Arguments:

- `<fen>` represents the current board state.
- The player argument is `Top` or `Bottom`.
- A move uses the format `start-target`, for example `a1-b2`.

### Initial Board

The standard initial FEN used by the project is:

```text
qqd1/qdp1/dpp1///1ppd/1pdq/1dqq
```

## 中文

这是一个用 Haskell 实现的 Martian Chess 作业项目。项目使用 Stack 管理构建、依赖和测试。

### 项目内容

核心模块：

- `src/Board.hs`：定义棋盘、单元格、玩家、位置、FEN 校验，以及 FEN 字符串和棋盘数据之间的转换。
- `src/Logic.hs`：实现棋子移动规则、执行移动、计分和胜负判断。
- `app/Main.hs`：提供命令行入口，用于调用移动生成、执行移动和胜负判断等功能。
- `test/Spec.hs`：Hspec 单元测试。
- `validate/Spec.hs`：验证测试。

### 环境要求

- Stack
- GHC 由 Stack 根据 `stack.yaml` 自动管理。

### 构建

```bash
stack build
```

清理构建产物：

```bash
stack clean
```

### 测试

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

### 命令行用法

构建后可以通过 `stack exec` 调用程序：

```bash
stack exec martian-chess -- pawnMoves "<fen>" Bottom a1 ""
stack exec martian-chess -- droneMoves "<fen>" Top b6 "a5-a6"
stack exec martian-chess -- queenMoves "<fen>" Bottom d1 ""
stack exec martian-chess -- makeMove "<fen>" "a1-b2"
stack exec martian-chess -- playerWon "<fen>" Top 3 2
```

参数说明：

- `<fen>` 表示当前棋盘状态。
- 玩家参数为 `Top` 或 `Bottom`。
- 移动格式为 `起点-终点`，例如 `a1-b2`。

### 初始棋盘

项目使用的标准初始 FEN：

```text
qqd1/qdp1/dpp1///1ppd/1pdq/1dqq
```
