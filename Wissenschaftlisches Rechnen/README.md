# Scientific Computing Assignments

This folder contains Python implementations for a scientific computing coursework series. The files are organized by assignment topic and focus on implementing numerical algorithms directly, often without using the high-level NumPy functions that would normally solve the task automatically.

## Contents

| File | Main topics |
| --- | --- |
| `main1.py` | Manual matrix multiplication, machine epsilon, matrix comparison, and 2D rotation matrices |
| `main2.py` | Gaussian elimination, back substitution, Cholesky decomposition, and tomography system setup |
| `main3.py` | Power iteration, image loading, PCA, eigenfaces, projection, and face identification |
| `main4.py` | Lagrange interpolation, Hermite interpolation, natural cubic splines, and periodic cubic splines |
| `main5.py` | DFT matrix construction, unitary matrix checks, harmonics, FFT, tone generation, and low-pass filtering |
| `main6.py` | Linear models, L2/perceptron/hinge losses, gradient-descent training, label preparation, and prediction |

## Requirements

- Python 3
- NumPy
- Matplotlib
- tqdm
- Course-provided helper modules such as `lib.py` and `tomograph.py` where required by the assignment files

Some files import helper modules that are usually provided by the course framework. If these helpers are missing locally, individual functions that do not depend on them can still be read or tested, but full assignment execution may require adding the original helper files.

## Usage

Run a file directly from this directory, for example:

```bash
python3 main4.py
```

For function-level testing, import the needed function in a Python shell or a separate test file:

```python
import numpy as np
from main1 import matrix_multiplication

a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])
print(matrix_multiplication(a, b))
```

## Notes

The implementations are written for learning and coursework submission. Many functions intentionally avoid direct library shortcuts so that the numerical method itself is visible in the code.

---

# Wissenschaftlisches Rechnen 作业

这个文件夹包含一组科学计算课程作业的 Python 实现。每个文件对应不同的数值计算主题，重点是手动实现算法本身，而不是直接调用 NumPy 中已经封装好的高级函数。

## 内容

| 文件 | 主要内容 |
| --- | --- |
| `main1.py` | 手写矩阵乘法、机器精度、矩阵近似比较、二维旋转矩阵 |
| `main2.py` | 高斯消元、回代法、Cholesky 分解、断层成像线性系统 |
| `main3.py` | 幂迭代、图像读取、PCA、Eigenfaces、人脸投影与识别 |
| `main4.py` | Lagrange 插值、Hermite 插值、自然三次样条、周期三次样条 |
| `main5.py` | DFT 矩阵、酉矩阵检查、谐波生成、FFT、音调生成、低通滤波 |
| `main6.py` | 线性模型、L2/感知机/Hinge 损失、梯度下降训练、标签处理、预测 |

## 运行要求

- Python 3
- NumPy
- Matplotlib
- tqdm
- 课程提供的辅助模块，例如部分文件中用到的 `lib.py` 和 `tomograph.py`

有些文件会导入课程框架提供的辅助模块。如果本地没有这些辅助文件，不依赖它们的单个函数仍然可以阅读或单独测试，但完整运行作业可能需要把原课程提供的 helper 文件一起放入目录。

## 使用方式

可以在该目录下直接运行某个文件，例如：

```bash
python3 main4.py
```

也可以在 Python shell 或单独的测试文件中导入某个函数进行测试：

```python
import numpy as np
from main1 import matrix_multiplication

a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])
print(matrix_multiplication(a, b))
```

## 说明

这些代码主要用于课程学习和作业提交。很多函数刻意不使用现成的库函数快捷方式，是为了展示数值算法的具体实现过程。
