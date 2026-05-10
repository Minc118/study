
import numpy as np

from lib import timedcall, plot_2d


def matrix_multiplication(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """󠀲󠀰󠀲󠀴󠀵
    Calculate product of two matrices a * b.

    Arguments:
    a : first matrix
    b : second matrix

    Return:
    c : matrix product a * b

    Raised Exceptions:
    ValueError: if matrix sizes are incompatible

    Side Effects:
    -

    Forbidden: numpy.dot, numpy.matrix, numpy.einsum
    """

    n, m_a = a.shape 
    m_b, p = b.shape

    # TODO: test if shape of matrices is compatible and raise error if not
    if m_a != m_b: #检查shape是否匹配，如果不匹配则报错，报错用ValueError，raise是用来抛出异常的关键字，他等同于throw
        raise ValueError("Error! matrix sizes are incompatible")
    # Initialize result matrix with zeros
    c = np.zeros((n, p))

    # TODO: Compute matrix product without the usage of numpy.dot()
    # 使用三重循环实现矩阵乘法，外层循环遍历结果矩阵的行，中间循环遍历结果矩阵的列，内层循环计算对应位置的值
    for i in range( n):
        for j in range( p ):
            for h in range( m_a ):
                c[i, j] = c[i, j] + (a[i, h] * b[h, j]) #计算c[i,j]的值，累加a的第i行和b的第j列对应元素的乘积
    return c


def compare_multiplication(nmax: int, n: int) -> dict:
    """󠀲󠀰󠀲󠀴󠀵
    Compare performance of numpy matrix multiplication (np.dot()) and matrix_multiplication.

    Arguments:
    nmax : maximum matrix size to be tested
    n : step size for matrix sizes

    Return:
    tr_dict : numpy and matrix_multiplication timings and results {"timing_numpy": [numpy_timings],
    "timing_mat_mult": [mat_mult_timings], "results_numpy": [numpy_results], "results_mat_mult": [mat_mult_results]}

    Raised Exceptions:
    -

    Side effects:
    Generates performance plots.
    """

    x, y_mat_mult, y_numpy, r_mat_mult, r_numpy = [], [], [], [], [] #初始化五个空列表，分别用于存储矩阵大小、矩阵乘法函数的时间、numpy乘法的时间、矩阵乘法函数的结果和numpy乘法的结果
    tr_dict = dict(timing_numpy=y_numpy, timing_mat_mult=y_mat_mult, results_numpy=r_numpy, results_mat_mult=r_mat_mult)
    #创建一个字典tr_dict，用于存储不同方法的时间和结果，键分别为"timing_numpy"、"timing_mat_mult"、"results_numpy"和"results_mat_mult"，对应的值是之前初始化的空列表
    # TODO: Can be removed if matrices a and b are created in loop 因为矩阵a和b在循环内创建，所以这两行可以删除
    # a = np.ones((2, 2)) 
    # b = np.ones((2, 2))

    for m in range(2, nmax, n):

        # TODO: Create random mxm matrices a and b
        a = np.random.rand( m, m) #生成一个m行m列的随机矩阵a，元素值在0到1之间均匀分布,np.random.rand()函数用于生成指定形状的随机数数组
        b = np.random.rand(m, m ) #生成一个m行m列的随机矩阵b，元素值在0到1之间均匀分布

        # Execute functions and measure the execution time
        time_mat_mult, result_mat_mult = timedcall(matrix_multiplication, a, b)
        time_numpy, result_numpy = timedcall(np.dot, a, b)

        # Add calculated values to lists
        x.append(m)
        y_numpy.append(time_numpy)
        y_mat_mult.append(time_mat_mult)
        r_numpy.append(result_numpy)
        r_mat_mult.append(result_mat_mult)

    # Plot the computed data
    plot_2d(x_data=x, y_data=[y_mat_mult, y_numpy], labels=["matrix_mult", "numpy"],
            title="NumPy vs. for-loop matrix multiplication",
            x_axis="Matrix size", y_axis="Time", x_range=[2, nmax])

    return tr_dict


def machine_epsilon(fp_format: np.dtype) -> np.number:
    """󠀲󠀰󠀲󠀴󠀵
    Calculate the machine precision for the given floating point type.

    Arguments:
    fp_format : floating point format, e.g. float32 or float64

    Return:
    eps : calculated machine precision

    Raised Exceptions:
    -

    Side Effects:
    Prints out iteration values.

    Forbidden: numpy.finfo
    """
    #es gibt 2 Methoden um die Maschinengenauigkeit zu bestimmen.
    # Methode 1: Additionsmethode
    # Methode 2: Multiplikationsmethode
    # Additionsmethode是通过不断减小一个数eps，直到1 + eps等于1为止，来确定机器精度的方法。
    # Multiplikationsmethode是通过不断减小一个数eps，直到1 * eps等于0为止，来确定机器精度的方法。

    # TODO: create epsilon element with correct initial value and data format fp_format
    eps = fp_format.type(1.0)


    # Create necessary variables for iteration
    one = fp_format.type(1.0) #创建浮点数1.0，数据类型为fp_format， 因为后续计算中需要用到1.0
    two = fp_format.type(2.0) #创建浮点数2.0，数据类型为fp_format，fp_format是函数的参数，表示浮点数的格式，可以是float32或float64
    i = 0

    print('  i  |       2^(-i)        |  1 + 2^(-i)  ')
    print('  ----------------------------------------')

    # TODO: determine machine precision without the use of numpy.finfo()
    # 有两种方法来可以写，
    while one + eps != one:
        letzteps = eps #保存上一次的eps值
        eps =eps / two #将eps除以2，逐渐减小eps的值
        i += 1 #迭代计数器加1
    

    print('{0:4.0f} |  {1:16.8e}   | equal 1'.format(i, eps))
    return letzteps



def close(a: np.ndarray, b: np.ndarray, eps: np.number=1e-08) -> bool:
    """󠀲󠀰󠀲󠀴󠀵
    Compare two floating point matrices. 

    Arguments:
    a : first matrix
    b : second matrix
    eps: tolerance

    Return:
    c : if a is close to b (within the tolerance)

    Raised Exceptions:
    ValueError: if matrix sizes are incompatible

    Side Effects:
    -

    Forbidden: numpy.isclose, numpy.allclose
    """
    isclose = False
    # TODO: check if a and b are compareable 形状必须相同，否则没法逐个元素比较
    if a.shape != b.shape:
        raise ValueError("Error! Shapes of matrices are not compatible")

    # TODO: check if all entries in a are close to the corresponding entry in b
    unterschied = a - b #计算矩阵a和b的差
    unterschiedWert = np.abs ( unterschied ) #计算矩阵a和b的差的绝对值
    if np.all( unterschiedWert <eps ): #检查差的绝对值是否都小于给定的容差eps
        isclose =True #如果都小于eps，则认为矩阵a和b是接近的，返回True
        #因为numpy.all()函数用于检查数组中的所有元素是否都满足某个条件，如果都满足则返回True，否则返回False

    return isclose


def rotation_matrix(theta: float) -> np.ndarray:
    """
    Create 2x2 rotation matrix around angle theta.

    Arguments:
    theta : rotation angle (in degrees)

    Return:
    r : rotation matrix

    Raised Exceptions:
    -

    Side Effects:
    -
    """

    # create empty matrix
    r = np.zeros((2, 2)) #创建一个2行2列的零矩阵，用于存储旋转矩阵

    # TODO: convert angle to radians
    angleToRadian = np.deg2rad(theta ) #将角度转换为弧度

    # TODO: calculate diagonal terms of matrix
    r[0, 0] = np.cos(angleToRadian ) #计算旋转矩阵的第一个对角线元素, np.cos()函数用于计算余弦值 0,0 表示矩阵的第一行第一列元素
    r[1, 1] = np.cos( angleToRadian ) #计算 旋转矩阵的第二个对角线元素 1,1 表示矩阵的第二行第二列元素

    # TODO: off-diagonal terms of matrix
    r[0, 1] = -np.sin( angleToRadian ) #计算旋转矩阵的第一个非对角线元素，np.sin()函数用于计算正弦值 0,1 表示矩阵的第一行第二列元素
    r[1, 0] = np.sin( angleToRadian ) #计算旋转矩阵的第二个非对角线元素，np.sin()函数用于计算正弦值 1,0 表示矩阵的第二行第一列元素

    return r


def inverse_rotation(theta: float) -> np.ndarray:
    """󠀲󠀰󠀲󠀴󠀵
    Compute inverse of the 2d rotation matrix that rotates a 
    given vector by theta.
    
    Arguments:
    theta: rotation angle
    
    Return:
    Inverse of the rotation matrix

    Forbidden: numpy.linalg.inv, numpy.linalg.solve
    """

    # TODO: compute inverse rotation matrix

    return rotation_matrix(theta).T #逆旋转矩阵等于旋转角度取负的旋转矩阵 .T表示矩阵的转置，旋转矩阵的转置等于其逆矩阵，因为旋转矩阵是正交矩阵，所以它的逆矩阵等于它的转置。

if __name__ == '__main__':

    print("All requested functions for󠀲󠀰󠀲󠀴󠀵 the assignment have to be implemented in this file and uploaded to the "
          "server for the grading.\nTo test your implemented functions you can "
          "implement/run tests in the file tests.py (> python3 -v test.py [Tests.<test_function>]).")

# TODO: Replace this with a thoughful comment
