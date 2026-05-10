import numpy as np


####################################################################################################
# Exercise 1: Interpolation

def lagrange_interpolation(x: np.ndarray, y: np.ndarray) -> (np.poly1d, list):
    """
    Generate Lagrange interpolation polynomial.

    Arguments:
    x: x-values of interpolation points
    y: y-values of interpolation points

    Return:
    polynomial: polynomial as np.poly1d object
    base_functions: list of base polynomials
    """

    assert (x.size == y.size)

    polynomial = np.poly1d(0)
    base_functions = []

    # 生成拉格朗日基多项式和插值多项式
    # 拉格朗日插值法的基多项式L_i(x)定义为：
    # L_i(x) = ∏ (x - x_j) / (x_i - x_j)  (j ≠ i)
    # 插值多项式P(x)定义为：
    # P(x) = Σ y_i * L_i(x)
    # 其中∏表示乘积，Σ表示求和
    # 这里我们使用numpy的poly1d类来表示多项式
    # 基多项式L_i(x)是一个多项式，我们通过乘积的方式构造它
    # 插值多项式P(x)是所有基多项式乘以对应y值的加权和
    # np.poly1d类允许我们方便地进行多项式的加法和乘法运算,它的原理是将多项式的系数存储在一个数组中，并提供了重载的运算符来实现多项式的加法和乘法

    # TODO: Generate Lagrange base polynomials and interpolation polynomial
    for i in range(len(x)):
        # 我使用拉格朗日插值法的基函数公式来构造每个基多项式
        lagPoly = np.poly1d(1) # 初始化为常数多项式1
        for j in range(len(x)): # 遍历所有节点
            if i != j: # 排除当前节点
                lagPoly *= np.poly1d([1, -x[j]]) / (x[i] - x[j]) # 构造基多项式
        base_functions.append(lagPoly) # 保存基多项式，以便返回，lagPoly是一个np.poly1d对象，表示拉格朗日基多项式L_i(x)
        # 将第i个基多项式乘以对应的y值，并加到插值多项式中
        polynomial += y[i] * lagPoly

    return polynomial, base_functions




def hermite_cubic_interpolation(x: np.ndarray, y: np.ndarray, yp: np.ndarray) -> list:
    """
    Compute hermite cubic interpolation spline

    Arguments:
    x: x-values of interpolation points
    y: y-values of interpolation points
    yp: derivative values of interpolation points

    Returns:
    spline: list of np.poly1d objects, each interpolating the function between two adjacent points
    """

    assert (x.size == y.size == yp.size)

    spline = []

    # 构造Hermite插值多项式的系数矩阵
    # 每个区间使用一个三次多项式进行插值，满足函数值和导数值的匹配条件
    # 每个多项式有4个系数，需要4个方程来确定
    # 每个区间的多项式需要满足以下条件：
    # 1. 在左端点处函数值匹配：S_i(x_i) = y_i
    # 2. 在左端点处导数值匹配：S_i'(x_i) = yp_i
    # 3. 在右端点处函数值匹配：S_i(x_{i+1}) = y_{i+1}
    # 4. 在右端点处导数值匹配：S_i'(x_{i+1}) = yp_{i+1} 
    # TODO compute piecewise interpolating cubic polynomials
    for i in range(len(x) - 1):
        # 构造Hermite插值多项式的系数矩阵
        matrix = np.array([[1, x[i], x[i]**2, x[i]**3],
                      [0, 1, 2*x[i], 3*x[i]**2],
                      [1, x[i+1], x[i+1]**2, x[i+1]**3],
                      [0, 1, 2*x[i+1], 3*x[i+1]**2]])
        constant = np.array([y[i], yp[i], y[i+1], yp[i+1]])
        coefficients = np.linalg.solve(matrix, constant)  # 求解系数
        spline.append(np.poly1d(coefficients[::-1]))  # 将系数反转以符合np.poly1d的要求

    return spline



####################################################################################################
# Exercise 2: Animation

def natural_cubic_interpolation(x: np.ndarray, y: np.ndarray) -> list:
    """
    Intepolate the given function using a spline with natural boundary conditions.

    Arguments:
    x: x-values of interpolation points
    y: y-values of interpolation points

    Return:
    spline: list of np.poly1d objects, each interpolating the function between two adjacent points
    """

    assert (x.size == y.size)
    #线性方程组的构造，基础的是每个区间的三次多项式需要满足插值条件、一阶导数连续性条件、二阶导数连续性条件以及自然边界条件
    #每个区间的三次多项式可以表示为S_i(x) = a_i + b_i*(x - x_i) + c_i*(x - x_i)^2 + d_i*(x - x_i)^3
    #其中a_i, b_i, c_i, d_i是需要确定的系数
    #总共有n-1个区间，每个区间有4个系数，因此总共有4*(n-1)个未知数
    #线性方程组的方程数量也必须是4*(n-1)，以确保有唯一解
    #插值条件提供了2*(n-1)个方程，一阶导数连续性条件提供了(n-2)个方程，二阶导数连续性条件也提供了(n-2)个方程，自然边界条件提供了2个方程
    #总方程数为2*(n-1) + (n-2) + (n-2) + 2 = 4*(n-1)，满足要求
    # TODO construct linear system with natural boundary conditions
    #我需要为每个区间构造一个三次多项式，并确保在节点处连续且具有连续的一阶和二阶导数。n是节点数，A是系数矩阵，b是常数向量。
    n= len(x) # 节点数
    A = np.zeros((4*(n-1), 4*(n-1))) # 系数矩阵
    b = np.zeros(4*(n-1)) # 常数向量
    # 构造线性方程组
    for i in range(n-1):
        xi, xi1 = x[i], x[i+1]
        yi, yi1 = y[i], y[i+1]

        # 插值条件
        A[4*i][4*i:4*i+4] = [1, xi, xi**2, xi**3]  # S_i(x_i) = y_i
        b[4*i] = yi

        A[4*i+1][4*i:4*i+4] = [1, xi1, xi1**2, xi1**3]  # S_i(x_{i+1}) = y_{i+1}
        b[4*i+1] = yi1

        # 一阶导数连续性条件
        if i < n - 2:
            A[4*i+2][4*i:4*i+4] = [0, 1, 2*xi1, 3*xi1**2]
            A[4*i+2][4*i+4:4*i+8] = [0, -1, -2*xi1, -3*xi1**2]
            b[4*i+2] = 0

        # 二阶导数连续性条件
        if i < n - 2:
            A[4*i+3][4*i:4*i+4] = [0, 0, 2, 6*xi1]
            A[4*i+3][4*i+4:4*i+8] = [0, 0, -2, -6*xi1]
            b[4*i+3] = 0

    # 自然边界条件: S''(x_0) = 0 和 S''(x_n) = 0
    A[-2][0:4] = [0, 0, 2, 6*x[0]]
    A[-1][-4:] = [0, 0, 2, 6*x[-1]]
    b[-2:] = [0, 0]

    # TODO solve linear system for the coefficients of the spline
    # 使用numpy的线性代数求解器来求解线性方程组，得到每个区间的多项式系数，然后将这些系数存储在spline列表中，以便返回
    coefficients = np.linalg.solve(A, b)
    spline = []
    # TODO extract local interpolation coefficients from solution
    for i in range(n-1): # 遍历每个区间，提取对应的多项式系数
        coeffsi = coefficients[4*i:4*i+4] # 提取第i个区间的系数
        spline.append(np.poly1d(coeffsi[::-1]))  # 将系数反转以符合np.poly1d的要求

    return spline


def periodic_cubic_interpolation(x: np.ndarray, y: np.ndarray) -> list:
    """
    Interpolate the given function with a cubic spline and periodic boundary conditions.

    Arguments:
    x: x-values of interpolation points
    y: y-values of interpolation points

    Return:
    spline: list of np.poly1d objects, each interpolating the function between two adjacent points
    """

    assert (x.size == y.size)
                     
    # TODO: construct linear system with periodic boundary conditions
    n= len(x) # 节点数  
    A = np.zeros((4*(n-1), 4*(n-1))) # 系数矩阵
    b = np.zeros(4*(n-1)) # 常数向量
    # 构造线性方程组
    for i in range(n-1): # 遍历每个区间
        # 插值条件
        xi, xi1 = x[i], x[i+1]
        yi, yi1 = y[i], y[i+1]

        A[4*i][4*i:4*i+4] = [1, xi, xi**2, xi**3]  # S_i(x_i) = y_i
        b[4*i] = yi

        A[4*i+1][4*i:4*i+4] = [1, xi1, xi1**2, xi1**3]  # S_i(x_{i+1}) = y_{i+1}
        b[4*i+1] = yi1

        # 一阶导数连续性条件
        if i < n - 2: # 最后一个区间不需要,因为它的右端点是第一个区间的左端点,已经在第一个区间的方程中考虑过了
            A[4*i+2][4*i:4*i+4] = [0, 1, 2*xi1, 3*xi1**2]
            A[4*i+2][4*i+4:4*i+8] = [0, -1, -2*xi1, -3*xi1**2]
            b[4*i+2] = 0

        # 二阶导数连续性条件
        if i < n - 2: 
            A[4*i+3][4*i:4*i+4] = [0, 0, 2, 6*xi1]
            A[4*i+3][4*i+4:4*i+8] = [0, 0, -2, -6*xi1]
            b[4*i+3] = 0

    # 周期边界条件: S'(x_0) = S'(x_n) 和 S''(x_0) = S''(x_n)
    A[-2][1:4]= [1, 2*x[0], 3*x[0]**2]  # S_0'(x_0)
    A[-2][-3:]=[-1, -2*x[-1], -3*x[-1]**2]  # -S_{n-2}'(x_n)
    b[-2]=0

    A[-1][2:4]= [2, 6*x[0]]  # S_0''(x_0)
    A[-1][-2:]= [-2, -6*x[-1]]
    b[-1]=0

    # TODO solve linear system for the coefficients of the spline
    coefficients = np.linalg.solve(A, b)
    spline = []
    # TODO extract local interpolation coefficients from solution
    for i in range(n-1): # 遍历每个区间，提取对应的多项式系数
        coeffsi = coefficients[4*i:4*i+4] # 提取第i个区间的系数
        spline.append(np.poly1d(coeffsi[::-1]))  # 将系数反转以符合np.poly1d的要求

    return spline


if __name__ == '__main__':

    x = np.array( [1.0, 2.0, 3.0, 4.0])
    y = np.array( [3.0, 2.0, 4.0, 1.0])

    splines = natural_cubic_interpolation( x, y)

    # # x-values to be interpolated
    # keytimes = np.linspace(0, 200, 11)
    # # y-values to be interpolated
    # keyframes = [np.array([0., -0.05, -0.2, -0.2, 0.2, -0.2, 0.25, -0.3, 0.3, 0.1, 0.2]),
    #              np.array([0., 0.0, 0.2, -0.1, -0.2, -0.1, 0.1, 0.1, 0.2, -0.3, 0.3])] * 5
    # keyframes.append(keyframes[0])
    # splines = []
    # for i in range(11):  # Iterate over all animated parts
    #     x = keytimes
    #     y = np.array([keyframes[k][i] for k in range(11)])
    #     spline = natural_cubic_interpolation(x, y)
    #     if len(spline) == 0:
    #         animate(keytimes, keyframes, linear_animation(keytimes, keyframes))
    #         self.fail("Natural cubic interpolation not implemented.")
    #     splines.append(spline)

    print("All requested functions for the assignment have to be implemented in this file and uploaded to the "
          "server for the grading.\nTo test your implemented functions you can "
          "implement/run tests in the file tests.py (> python3 -v test.py [Tests.<test_function>]).")
