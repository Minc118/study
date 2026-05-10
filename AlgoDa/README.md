# AlgoDa

## English

This directory contains Java homework submissions for the Algorithms and Data Structures course. The assignments are organized by weekly sheets (`Blatt00` to `Blatt07`) and include source code, assignment PDFs, local IntelliJ project files, grading result files, tests, and selected input data.

### Contents

| Directory | Main Topics | Important Files |
| --- | --- | --- |
| `Blatt00/` | Introductory Java exercise. | `src/Aufgabe0.java`, `Abgaben.txt`, `results_Blatt00.txt` |
| `Blatt01/` | Object-oriented geometry: vectors, shapes, polygons, convex polygons, triangles, tetragons, and regular polygons. | `src/Vector2D.java`, `src/Shape.java`, `src/Polygon.java`, `src/ConvexPolygon.java`, `src/Triangle.java`, `src/Tetragon.java`, `src/RegularPolygon.java` |
| `Blatt02/` | Stacks, queues, card comparison, decimal-to-binary conversion, and a simulation of the card game Bettelmann. | `src/Dec2Bin.java`, `src/Card.java`, `src/Bettelmann.java` |
| `Blatt03/` | Permutations, derangements, backtracking, and test-driven validation of given code. | `src/Permutation.java`, `src/Permutation1.java`, `src/PermutationVariation.java`, `src/PermutationTest.java` |
| `Blatt04/` | Tic-Tac-Toe board logic and game-state evaluation with alpha-beta pruning. | `src/Board.java`, `src/Position.java`, `src/TicTacToe.java`, `test/` |
| `Blatt05/` | Dynamic programming and recursion, including the Row of Bowls strategy problem and a genomics exercise. | `src/RowOfBowls.java`, `src/Genomics.java`, `src/*Test.java` |
| `Blatt06/` | Graph data structures, depth-first search, randomized DFS, maze generation, and visualization support. | `src/Graph.java`, `src/DepthFirstPaths.java`, `src/RandomDepthFirstPaths.java`, `src/Maze.java`, `src/GridGraph.java` |
| `Blatt07/` | Weighted graphs, Prim's minimum spanning tree algorithm, union-find, and MST-based clustering. | `src/EdgeWeightedGraph.java`, `src/PrimMST.java`, `src/Clustering.java`, `src/UF.java`, `src/iris*.txt`, `src/graph_*.txt` |

### Result Summary

The file `homework_results.txt` summarizes the grading status:

| Sheet | Points |
| --- | ---: |
| Blatt00 | 10 / 10 |
| Blatt01 | 100 / 100 |
| Blatt02 | 100 / 100 |
| Blatt03 | 100 / 100 |
| Blatt04 | 90 / 100 |
| Blatt05 | 100 / 100 |
| Blatt06 | 90 / 100 |
| Blatt07 | 35 / 100 |

Total listed semester points: `625 / 710` (`88.0%`). The recorded exam eligibility status is `YES`.

### Build and Run

There is no single build system for the whole directory. Each sheet is a small Java project and can be compiled from its `src/` directory.

Example:

```bash
cd Blatt04/src
javac *.java
java TicTacToe
```

Some sheets include JUnit tests. To run them, use the course-provided or IDE-provided JUnit setup. IntelliJ IDEA project files (`*.iml`) are included for several sheets.

### Notes

- Assignment PDFs and grading reports are kept together with the corresponding solutions.
- Some directories contain generated files such as `.class` files and `out/` folders. They reflect the local working state at the time of submission.
- The code is primarily written for coursework and learning purposes, so the structure follows the exercise sheets rather than a single production-style application layout.

## 中文

这个目录保存 Algorithms and Data Structures 课程的 Java 作业提交内容。作业按每周练习单分组，从 `Blatt00` 到 `Blatt07`，其中包含源码、题目 PDF、本地 IntelliJ 项目文件、评分结果、测试文件以及部分输入数据。

### 内容概览

| 目录 | 主要内容 | 重要文件 |
| --- | --- | --- |
| `Blatt00/` | Java 入门练习。 | `src/Aufgabe0.java`, `Abgaben.txt`, `results_Blatt00.txt` |
| `Blatt01/` | 面向对象几何：向量、图形、多边形、凸多边形、三角形、四边形和正多边形。 | `src/Vector2D.java`, `src/Shape.java`, `src/Polygon.java`, `src/ConvexPolygon.java`, `src/Triangle.java`, `src/Tetragon.java`, `src/RegularPolygon.java` |
| `Blatt02/` | 栈、队列、纸牌比较、十进制转二进制，以及 Bettelmann 纸牌游戏模拟。 | `src/Dec2Bin.java`, `src/Card.java`, `src/Bettelmann.java` |
| `Blatt03/` | 排列、错排、回溯，以及通过测试验证给定代码。 | `src/Permutation.java`, `src/Permutation1.java`, `src/PermutationVariation.java`, `src/PermutationTest.java` |
| `Blatt04/` | Tic-Tac-Toe 棋盘逻辑，以及使用 alpha-beta pruning 评估游戏局面。 | `src/Board.java`, `src/Position.java`, `src/TicTacToe.java`, `test/` |
| `Blatt05/` | 动态规划和递归，包括 Row of Bowls 策略问题和 Genomics 练习。 | `src/RowOfBowls.java`, `src/Genomics.java`, `src/*Test.java` |
| `Blatt06/` | 图数据结构、深度优先搜索、随机 DFS、迷宫生成和可视化辅助。 | `src/Graph.java`, `src/DepthFirstPaths.java`, `src/RandomDepthFirstPaths.java`, `src/Maze.java`, `src/GridGraph.java` |
| `Blatt07/` | 加权图、Prim 最小生成树、并查集，以及基于 MST 的聚类。 | `src/EdgeWeightedGraph.java`, `src/PrimMST.java`, `src/Clustering.java`, `src/UF.java`, `src/iris*.txt`, `src/graph_*.txt` |

### 成绩概览

`homework_results.txt` 中记录了评分汇总：

| 练习单 | 分数 |
| --- | ---: |
| Blatt00 | 10 / 10 |
| Blatt01 | 100 / 100 |
| Blatt02 | 100 / 100 |
| Blatt03 | 100 / 100 |
| Blatt04 | 90 / 100 |
| Blatt05 | 100 / 100 |
| Blatt06 | 90 / 100 |
| Blatt07 | 35 / 100 |

已记录的总分为 `625 / 710`，比例为 `88.0%`。考试资格状态记录为 `YES`。

### 编译与运行

整个目录没有统一的构建系统。每个 Blatt 都是一个小型 Java 项目，通常可以进入对应的 `src/` 目录单独编译。

示例：

```bash
cd Blatt04/src
javac *.java
java TicTacToe
```

部分练习单包含 JUnit 测试。运行测试时需要使用课程提供的 JUnit 环境，或者通过 IntelliJ IDEA 配置运行。多个练习单中保留了 IntelliJ IDEA 的 `*.iml` 文件。

### 备注

- 每个作业目录中保留了对应的题目 PDF 和评分结果。
- 部分目录包含 `.class` 文件和 `out/` 文件夹等生成产物，用于保留当时本地提交时的工作状态。
- 这些代码主要用于课程学习和作业提交，因此目录结构更接近练习单要求，而不是统一的生产项目结构。
