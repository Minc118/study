# Artificial Intelligence Course SS25

This folder contains Python coursework for an Artificial Intelligence / data analytics learning track. The assignments use NumPy, PyTorch, scikit-learn, Matplotlib, and pytest to practice optimization, neural networks, classification, regression, and bandit algorithms.

## Folder Structure

```text
ai-course-student-ss25/
├── 00/   Setup test assignment and basic Python function practice
├── 01/   Optimization with PyTorch autograd, finite differences, and linear equations
├── 02/   Neural network binary classification on the two-moons dataset
├── 03/   Discrete and continuous UCB bandits with neural-network bootstrapping
└── README.md
```

## Assignment Overview

| Folder | Main topics | Key files |
| --- | --- | --- |
| `00/` | Environment setup, pytest workflow, basic function implementation | `solution_00.py`, `module_1.py`, `tests/test_public.py` |
| `01/` | Gradient-based optimization, finite-difference gradients, analytical and SGD solutions for linear systems | `solution_01.py`, `tests/test_public.py` |
| `02/` | Fully connected neural network, binary classification, training loop, prediction, accuracy, decision-boundary plots | `solution_02.py`, `requirements_02.txt`, `assets/`, `tests/test_public.py` |
| `03/` | UCB for discrete bandits, neural-network regression, bootstrapping, continuous-action UCB | `solution_03.py`, `utils.py`, `tests/test_public.py` |

## Environment Setup

Create and activate a virtual environment from this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies for assignment 02:

```bash
python3 -m pip install -r 02/requirements_02.txt
```

Assignment 03 uses the same core Python stack: NumPy, PyTorch, Matplotlib, tqdm, and pytest.

## Running Tests

Run the public tests from each assignment folder:

```bash
cd 00
python3 -m pytest
```

```bash
cd 01
python3 -m pytest
```

```bash
cd 02
python3 -m pytest
```

```bash
cd 03
python3 -m pytest
```

## Generated Outputs

Some assignments can generate plots and PDF outputs after the required functions are implemented:

- `02/decision_boundary.pdf`: classifier decision boundary for the moons dataset
- `02/loss.pdf`: training loss curve
- `03/ucb_continuous.pdf`: continuous-action UCB visualization

## Notes

- The coursework is organized with one solution file per assignment.
- Public tests are included under each assignment folder.
- Virtual environments, Python caches, IDE files, and OS metadata are ignored through `.gitignore`.

---

# 人工智能课程 SS25

这个目录包含人工智能 / 数据分析方向的 Python 课程作业。作业使用 NumPy、PyTorch、scikit-learn、Matplotlib 和 pytest，覆盖优化、神经网络、分类、回归以及多臂老虎机算法。

## 目录结构

```text
ai-course-student-ss25/
├── 00/   环境测试作业与基础 Python 函数练习
├── 01/   PyTorch 自动求导、有限差分优化与线性方程求解
├── 02/   基于 two-moons 数据集的神经网络二分类
├── 03/   离散与连续动作空间下的 UCB 多臂老虎机算法
└── README.md
```

## 作业内容概览

| 文件夹 | 主要内容 | 关键文件 |
| --- | --- | --- |
| `00/` | 环境配置、pytest 测试流程、基础函数实现 | `solution_00.py`, `module_1.py`, `tests/test_public.py` |
| `01/` | 梯度优化、有限差分梯度、线性方程的解析解和 SGD 解法 | `solution_01.py`, `tests/test_public.py` |
| `02/` | 全连接神经网络、二分类、训练循环、预测、准确率计算、决策边界可视化 | `solution_02.py`, `requirements_02.txt`, `assets/`, `tests/test_public.py` |
| `03/` | 离散 UCB、多臂老虎机、神经网络回归、Bootstrap、连续动作 UCB | `solution_03.py`, `utils.py`, `tests/test_public.py` |

## 环境配置

在该目录下创建并激活虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

安装第 02 次作业所需依赖：

```bash
python3 -m pip install -r 02/requirements_02.txt
```

第 03 次作业使用相同的核心 Python 工具栈：NumPy、PyTorch、Matplotlib、tqdm 和 pytest。

## 运行测试

在每个作业文件夹中运行公开测试：

```bash
cd 00
python3 -m pytest
```

```bash
cd 01
python3 -m pytest
```

```bash
cd 02
python3 -m pytest
```

```bash
cd 03
python3 -m pytest
```

## 生成的结果文件

在补全对应函数后，部分作业可以生成图像和 PDF 结果：

- `02/decision_boundary.pdf`：moons 数据集分类器的决策边界
- `02/loss.pdf`：训练损失曲线
- `03/ucb_continuous.pdf`：连续动作 UCB 可视化

## 说明

- 作业按每次练习一个 solution 文件的方式组织。
- 每个作业文件夹下都包含公开测试。
- `.gitignore` 已忽略虚拟环境、Python 缓存、IDE 文件和系统元数据。
