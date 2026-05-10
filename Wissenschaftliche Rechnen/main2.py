
import numpy as np
import tomograph


####################################################################################################
# Exercise 1: Gaussian elimination

def gaussian_elimination(A: np.ndarray, b: np.ndarray, use_pivoting: bool = True) -> (np.ndarray, np.ndarray):
    """
    Gaussian Elimination of Ax=b with or without pivoting.
    实现带或不带主元选择的高斯消元法
    Arguments:
    A : matrix, representing left side of equation system of size: (m,m)
    b : vector, representing right hand side of size: (m, )
    use_pivoting : flag if pivoting should be used

    Return:
    A : reduced result matrix in row echelon form (type: np.ndarray, size: (m,m))
    b : result vector in row echelon form (type: np.ndarray, size: (m, ))

    Raised Exceptions:
    ValueError: if matrix and vector sizes are incompatible, matrix is not square or pivoting is disabled but necessary

    Side Effects:
    -

    Forbidden:
    - numpy.linalg.*
    """
    #创建输入矩阵和向量的副本，以免修改原始数据
    # Create copies of input matrix and vector to leave them unmodified
    A = A.copy()
    b = b.copy()

    #检查举证A是否为方阵，b是否为一维或二维向量，并检查它们的形状是否兼容
    # TODO: Test if shape of matrix and vector is compatible and raise ValueError if not
    if A.ndim !=2 or b.ndim !=1: #这么做是为了简化检查过程，确保A是二维矩阵，b是一维向量，否则抛出异常
        raise ValueError("a and b not compatible, wrong dimensions, A must be 2D and b 1D")
    m, n= A.shape #获取矩阵A的行数和列数
    if m !=n: #检查矩阵A是否为方阵
        raise ValueError("matrix A is not square")
    if b.shape[0] !=m: #检查向量b的长度是否与矩阵A的行数匹配
        raise ValueError("a and b not compatible, wrong shapes")
    
    eps = np.finfo(float).eps #获取浮点数的机器精度，用于后续的数值稳定性检查,skript 1.5.2

    # TODO: Perform gaussian elimination
    #执行高斯消元法,遍历每一列
    for k in range(n):
        #如果启用主元选择
        if use_pivoting:
            #找到当前列中绝对值最大的元素所在的行索引
            max_index = np.argmax(np.abs(A[k:,k])) +k
            #如果该最大值小于机器精度，说明矩阵可能是奇异的，抛出异常
            if np.abs(A[max_index, k]) < eps:
                raise ValueError("matrix is singular to working precision")
            #如果最大值不在当前行，则交换当前行和最大值所在的行
            if max_index != k:
                A[[k, max_index]]= A[[max_index,k]]
                b[[k, max_index]] =b[[max_index, k]]
        else:
            #如果不使用主元选择，检查当前主元是否接近零，如果是则抛出异常
            if np.abs(A[k, k]) < eps:
                raise ValueError("0 is pivoting element, but pivoting disabled")

        #对当前列以下的所有行进行消元操作
        for i in range(k + 1, m):
            factor = A[i, k]/ A[k, k] #计算消元因子
            A[i, k:] -= factor* A[k, k:] #更新当前行的元素
            #A[i, k] = 0.0 #将当前列的元素显式设为0（可选）
            b[i] -= factor *b[k] #更新对应的b向量元素

        #     # --- 消元步骤 (Elimination) ---
        # # 只有当 k 不是最后一行时才需要进行消元操作
        # if k < n - 1:
        #     # 向量化操作：同时更新第 k 行下方的所有行
        #     # 计算消元因子: factor = A[i, k] / A[k, k]
        #     factors = A[k+1:, k] / A[k, k]
            
        #     # 更新 A 的剩余部分 (利用广播机制)
        #     # A[i, j] = A[i, j] - factor * A[k, j]
        #     # np.newaxis 用于让 factors 变成列向量
        #     A[k+1:, k:] -= factors[:, np.newaxis] * A[k, k:]
            
        #     # 更新向量 b
        #     b[k+1:] -= factors * b[k]
            
        #     # 为了数值美观和准确，将第 k 列下方显式置为 0
        #     A[k+1:, k] = 0.0

    return A, b


def back_substitution(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Back substitution for the solution of a linear system in row echelon form.

    Arguments:
    A : matrix in row echelon representing linear system
    b : vector, representing right hand side

    Return:
    x : solution of the linear system

    Raised Exceptions:
    ValueError: if matrix/vector sizes are incompatible or no/infinite solutions exist

    Side Effects:
    -

    Forbidden:
    - numpy.linalg.*
    """

    # TODO: Test if shape of matrix and vector is compatible and raise ValueError if not
    if A.ndim !=2 or b.ndim !=1:
        raise ValueError("a and b not compatible, wrong dimensions, A must be 2D and b 1D")
    m, n=A.shape
    if m !=n:
        raise ValueError("matrix A is not square")
    if b.shape[0] !=m:
        raise ValueError("a and b not compatible, wrong shapes")

    # TODO: Initialize solution vector with proper size
    x = np.zeros(n) #初始化解向量x，大小与矩阵A的列数相同
    eps = np.finfo(float).eps #获取浮点数的机器精度，用于数值稳定性检查,skript 1.5.2

    # TODO: Run backsubstitution and fill solution vector, raise ValueError if no/infinite solutions exist

    #遍历矩阵A的行，从最后一行开始向上,进行回代计算,计算解向量x的每个元素,从最后一个元素开始,逐步向前计算
    for i in range (n-1, -1,-1):
        diaglogal = A[i,i] #获取当前行的对角线元素
        if np.abs(diaglogal) <eps: #检查对角线元素是否接近零,如果是则抛出异常,说明没有唯一解
            raise ValueError("no solution or infinite solutions exist")
        
        # 计算已知项的加权和: sum(A[i, j] * x[j]) for j > i
        # 使用切片 A[i, i+1:] 获取当前行对角线右侧的元素
        # 使用切片 x[i+1:] 获取下方已经解出的 x 值
        # np.dot 计算它们的点积
        sum_known = np.dot(A[i,i+1:], x[i+1:]) #计算当前行已知部分的贡献,即当前行中已计算出的解向量元素与对应矩阵元素的乘积之和

        # 计算当前 x[i]
        # 公式: x_i = (b_i - sum) / A_ii
        x[i] = (b[i]- sum_known) /diaglogal #计算当前行对应的解向量元素
    
    return x


####################################################################################################
# Exercise 2: Cholesky decomposition

def compute_cholesky(M: np.ndarray) -> np.ndarray:
    """
    Compute Cholesky decomposition of a matrix

    Arguments:
    M : matrix, symmetric and positive (semi-)definite

    Raised Exceptions:
    ValueError: L is not symmetric and psd

    Return:
    L :  Cholesky factor of M

    Forbidden:
    - numpy.linalg.*
    """

    # TODO check for symmetry and raise an exception of type ValueError
    (n, m) = M.shape

    if n != m: #检查矩阵L是否为方阵,n为行数,m为列数
        raise ValueError("Matrix is not square")
    if M.ndim !=2: #检查矩阵L是否为二维矩阵, ndim属性返回数组的维数, !=2表示不是二维矩阵
        raise ValueError("Matrix isnot 2D")
    if not np.allclose(M, M.T): #检查矩阵是否对称, np.allclose用于判断两个数组是否在一定容差范围内相等
        raise ValueError("Matrix is not symmetric")
    


    # TODO build the factorization and raise a ValueError in case of a non-positive definite input matrix

    L = np.zeros((n, n)) #初始化Cholesky因子矩阵L为零矩阵,大小与输入矩阵M相同,n为矩阵的行数或列数
    eps = np.finfo(float).eps #获取浮点数的机器精度，用于数值稳定性检查,skript 1.5.2

    for i in range(n): #遍历矩阵的每一行
        for j in range(i + 1): #遍历当前行的每一列, 直到对角元素
            if j!=0: #计算L[i,j]的值,根据Cholesky分解的公式
                sum_ij = np.dot(L[i, :j], L[j,:j]) #计算已知部分的加权和,即L矩阵中第i行和第j行前j个元素的点积,用于计算当前元素的值
            else:
                sum_ij =0.0 #当j为0时,前j个元素为空,加权和为0
            if i == j: #处理对角元素的情况
                diago = M[i, i] -sum_ij #计算对角元素的值,根据Cholesky分解的公式,减去已知部分的加权和,得到当前对角元素的值
                if diago < eps: #检查对角元素是否为正,如果不是则抛出异常,说明矩阵不是正定的
                    raise ValueError("Matrix is worry! nicht gut ausgesucht")
                L[i, j] = np.sqrt(diago) #计算对角元素的平方根,赋值给L矩阵的对应位置
            else: #处理非对角元素的情况
                L[i, j] = (M[i, j] -sum_ij)/ L[j,j] #计算非对角元素的值,根据Cholesky分解的公式,减去已知部分的加权和,再除以对应的对角元素,赋值给L矩阵的对应位置

    return L


def solve_cholesky(L: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Solve the system L L^T x = b where L is a lower triangular matrix

    Arguments:
    L : matrix representing the Cholesky factor #矩阵L，表示Cholesky因子
    b : right hand side of the linear system #线性系统的右侧向量

    Raised Exceptions:
    ValueError: sizes of L, b do not match #尺寸不匹配
    ValueError: L is not lower triangular matrix #L不是下三角矩阵

    Return:
    x : solution of the linear system

    Forbidden:
    - numpy.linalg.*
    """

    # TODO Check the input for validity, raising a ValueError if this is not the case
    (n, m) = L.shape #获取矩阵L的形状,n为行数,m为列数

    if n !=m: #检查矩阵L是否为方阵
        raise ValueError("L isnot square")
    if L.ndim !=2 or b.ndim !=1: #检查矩阵L是否为二维矩阵
        raise ValueError("L isnot 2D or b isnot 1D")
    if b.shape[0] !=n: #检查向量b的长度是否与矩阵L的行数匹配
        raise ValueError("L and b sizes donot match")
    if not np.allclose(L, np.tril(L)): #检查矩阵L是否为下三角矩阵, np.tril用于提取矩阵的下三角部分
        raise ValueError("L isnot lower triangular matrix")
    


    # TODO Solve the system by forward- and backsubstitution
    x = np.zeros(m)
    # Forward substitution to solve Ly = b
    y = np.zeros(n) #初始化中间变量y,大小与矩阵L的行数相同
    eps = np.finfo(float).eps #获取浮点数的机器精度，用于数值稳定性检查,skript 1.5.2

    for i in range(n): #遍历矩阵L的每一行
        if np.abs(L[i, i]) < eps: #检查对角元素是否接近零,如果是则抛出异常,说明矩阵L是奇异的
            raise ValueError("matrix L is singular")
        sum_iy = np.dot(L[i, :i], y[:i]) #计算已知部分的加权和,即L矩阵中第i行前i个元素与y向量中前i个元素的点积
        y[i] = (b[i] - sum_iy) /L[i, i] #计算y向量的当前元素,根据前向替代的公式

    # Back substitution to solve L^T x = y
    x = back_substitution(L.T, y) #调用之前实现的回代函数,传入L的转置矩阵和中间变量y,得到最终解向量x

    return x


####################################################################################################
# Exercise 3: Tomography

def setup_system_tomograph(n_shots: np.int64, n_rays: np.int64, n_grid: np.int64) -> (np.ndarray, np.ndarray):
    """
    Set up the linear system describing the tomographic reconstruction

    Arguments:
    n_shots : number of different shot directions #不同投射方向的数量
    n_rays  : number of parallel rays per direction #每个方向的平行射线数量
    n_grid  : number of cells of grid in each direction, in total n_grid*n_grid cells #每个方向网格的单元格数量，总共有n_grid*n_grid个单元格

    Return:
    L : system matrix #系统矩阵
    g : measured intensities #测量强度

    Raised Exceptions:
    -

    Side Effects:
    -

    Forbidden:
    -
    """

    # TODO: Initialize system matrix with proper size
    nequations =n_shots *n_rays  #计算方程的总数量,等于投射方向数量乘以每个方向
    nvariables = n_grid*n_grid  #计算变量的总数量,等于网格单元格数量的平方

    L = np.zeros((nequations, nvariables))  #初始化系统矩阵L为零矩阵,大小为方程数量乘以变量数量
    # TODO: Initialize intensity vector
    g = np.zeros(nequations)  #初始化强度向量g为零向量,大小为方程数量

    # TODO: Iterate over equispaced angles, take measurements, and update system matrix and sinogram #遍历等间距角度，进行测量，并更新系统矩阵和正弦图
    theta = 0
    # Take a measurement with the tomograph from direction r_theta. #theta是测量方向的角度
    # intensities: measured intensities for all <n_rays> rays of the measurement. intensities[n] contains the intensity for the n-th ray #n_rays是每个测量的射线数量
    # ray_indices: indices of rays that intersect a cell #ray_indices:与单元格相交的射线索引
    # isect_indices: indices of intersected cells #isect_indices:相交单元格的索引
    # lengths: lengths of segments in intersected cells#长度:相交单元格中段的长度
    # The tuple (ray_indices[n], isect_indices[n], lengths[n]) stores which ray has intersected which cell with which length. n runs from 0 to the amount of ray/cell intersections (-1) of this measurement. #元组(ray_indices[n], isect_indices[n], lengths[n])存储了哪条射线以多长的长度与哪个单元格相交。n从0运行到该测量的射线/单元格交点数量(-1)。
    for s, theta in enumerate(np.linspace(0.0, np.pi, n_shots, endpoint=False)):
        intensities, ray_indices, isect_indices, lengths = tomograph.take_measurement(n_grid, n_rays, theta)
        startrow_offset = s * n_rays  #计算当前投射方向的起始行偏移量,等于投射方向索引乘以每个方向的射线数量
        endrow_offset = startrow_offset + n_rays  #计算当前投射方向的结束行偏移量,等于起始行偏移量加上每个方向的射线数量

        g[startrow_offset:endrow_offset] =intensities  #将测量的强度值存储到强度向量g的对应位置
        globalinitial_index = startrow_offset +ray_indices  #计算全局初始索引,等于起始行偏移量加上射线索引
        L[globalinitial_index, isect_indices] +=lengths  #更新系统矩阵L,将相交单元格的长度加到对应的位置

    return [L, g]


def compute_tomograph(n_shots: np.int64, n_rays: np.int64, n_grid: np.int64) -> np.ndarray:
    """
    Compute tomographic image

    Arguments:
    n_shots : number of different shot directions #不同投射方向的数量
    n_rays  : number of parallel rays per direction #每个方向的平行射线数量
    n_grid  : number of cells of grid in each direction, in total n_grid*n_grid cells #每个方向网格的单元格数量，总共有n_grid*n_grid个单元格

    Return:
    tim : tomographic image #断层图像

    Raised Exceptions: 
    -

    Side Effects:
    -

    Forbidden:
    """

    # Setup the system describing the image reconstruction
    [L, g] = setup_system_tomograph(n_shots, n_rays, n_grid)

    # TODO: Solve for tomographic image using your Cholesky solver
    # (alternatively use Numpy's Cholesky implementation) #使用Cholesky求解器求解断层图像(或者使用Numpy的Cholesky实现)
    # Build the normal equations: L^T L x = L^T g #构建正规方程:L^T L x = L^T g
    A = L.T @ L  #计算正规方程的系数矩阵A,等于L的转置矩阵乘以L
    b = L.T @ g  #计算正规方程的右侧向量b,等于L的转置矩阵乘以g

    #用Cholesky分解求解正规方程
    Lcholeskyed = compute_cholesky(A)  #计算系数矩阵A的Cholesky分解,得到下三角矩阵Lcholeskyed
    x = solve_cholesky(Lcholeskyed, b)  #使用Cholesky求解器求解线性系统,得到解向量x

    # TODO: Convert solution of linear system to 2D image #将线性系统的解转换为二维图像
    tim = np.zeros((n_grid, n_grid))
    tim = x.reshape((n_grid, n_grid))  #将解向量x重塑为二维数组,大小为n_grid乘以n_grid

    return tim


if __name__ == '__main__':
    print("All requested functions for the assignment have to be implemented in this file and uploaded to the "
          "server for the grading.\nTo test your implemented functions you can "
          "implement/run tests in the file tests.py (> python3 -v test.py [Tests.<test_function>]).")

# TODO: Replace this with a justification of why your code is correct
# About Exercise 1 (gaussian_elimination + back_substitution):
# - In gaussian_elimination, I implemented the standard Gaussian elimination (Gauß-Elimination) as taught in class, performing only row operations (Zeilenoperationen), so the solution set of Ax=b remains unchanged.
# - If use_pivoting=True, I use np.argmax in each column to find the largest pivot element (Pivotisierung) and swap that row upward to avoid numerical instability caused by small pivots. If pivoting is off and a pivot is close to zero, I simply raise an error saying “pivoting is off but I can’t handle this,” honestly acknowledging the issue.
# - back_substitution is the usual Rückwärtseinsetzen (back substitution): starting from the last row upward, using
# x[i] = (b[i] - sum_{j>i} A[i,j]*x[j]) / A[i,i],
# where each step uses only the already computed x[j].
# If any diagonal entry is too small, I raise an error indicating that “the system does not have a unique solution.”
# About Exercise 2 (compute_cholesky + solve_cholesky):
# - compute_cholesky first checks whether M is a 2D square and symmetric (symmetrisch) matrix — the basic requirement for a Cholesky decomposition (Cholesky-Zerlegung).
# - When computing L, I use the Banachiewicz form:
# L_ii = sqrt(M_ii - sum_k L_ik^2)
# L_ij = (M_ij - sum_k L_ik * L_jk) / L_jj (for i>j)
# If any diagonal entry ≤ 0 occurs, I raise an error, indicating that the matrix is not positive definite (positiv definit), which matches the theory that “only symmetric positive definite matrices admit a Cholesky decomposition.”
# - In solve_cholesky, the equation L Lᵀ x = b is split into two steps:
# first forward substitution (Vorwärtseinsetzen) to solve Ly = b,
# then using the back_substitution function above to solve Lᵀx = y.
# This follows the standard procedure for solving linear systems via Cholesky factors, as taught in class.
# About Exercise 3 (setup_system_tomograph + compute_tomograph):
# - In setup_system_tomograph, I build the system matrix L according to the problem statement:
# each ray corresponds to one row, and each cell represents one unknown.
# The tomograph.take_measurement function returns the path lengths (Weglänge) of a ray through each cell, which I use as coefficients for L[row, col].
# The measured intensities go directly into g, with row indices computed via startrow_offset + ray_indices.
# - In compute_tomograph, I set up the least squares problem Lx ≈ g (Ausgleichsproblem) in the form of normal equations (Normalengleichungen):
# A = L.T @ L
# b = L.T @ g
# Then I solve A x = b using my own compute_cholesky and solve_cholesky functions.
# The resulting 1D vector x is finally reshaped with reshape((n_grid, n_grid)) into a 2D tomographic image tim.