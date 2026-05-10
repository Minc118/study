import numpy as np
import lib
import matplotlib as mpl


####################################################################################################
# Exercise 1: Power Iteration

def power_iteration(M: np.ndarray, epsilon: float = -1.0) -> (np.ndarray, list):
    """
    Compute largest eigenvector of matrix M using power iteration. It is assumed that the
    largest eigenvalue of M, in magnitude, is well separated.

    Arguments:
    M: matrix, assumed to have a well separated largest eigenvalue
    epsilon: epsilon used for convergence (default: 10 * machine precision)

    Return:
    vector: eigenvector associated with largest eigenvalue
    residuals : residual for each iteration step

    Raised Exceptions:
    ValueError: if matrix is not square

    Forbidden:
    numpy.linalg.eig, numpy.linalg.eigh, numpy.linalg.svd
    """
    if M.shape[0] != M.shape[1]:
        raise ValueError("Matrix not nxn")

    # TODO: set epsilon to default value if not set by user 
    #如果没有指定epsilon，则将其设定为10倍的机器精度，以确保迭代的收敛性和数值稳定性
    if epsilon == -1.0:#用户没有提供有效的epsilon值,<=0是为了防止用户传入负值或零
        epsilon = 10 * np.finfo(1.0).eps #机器精度，即浮点数在计算机中表示的最小差值，np.finfo(float).eps返回浮点数类型的机器精度

    # TODO: normalized random vector of proper size to initialize iteration
    #初始化一个随机向量，使用随机向量是为了避免初始向量与某些特定的特征向量对齐，从而确保迭代过程的有效性
    #归一化（normalization）是为了确保向量的长度为1，这有助于防止数值溢出或下溢，并保持迭代过程的稳定性
    #对应skript4.4节的von Mises迭代法
    #np.zeros(1)只是一个占位符，实际实现中应替换为适当大小的随机向量
    #np.random.rand(M.shape[0])生成一个长度为M.shape[0]的随机向量
    vector = np.random.rand(M.shape[0])
    vector = vector / np.linalg.norm(vector)#np.linalg.norm(vector)计算向量的范数（长度），然后将向量除以其范数以实现归一化

    # Initialize residual list and residual of current eigenvector estimate
    residuals = []
    residual = 2.0 * epsilon

    # Perform power iteration
    while residual > epsilon:
        # TODO: implement power iteration
        #矩阵向量乘法（matrix-vector multiplication）是线性代数中的基本操作，用于将矩阵应用于向量，从而生成一个新的向量
        #v_{k+1} = M * v_k - 是幂迭代法的核心步骤，通过将矩阵M应用于当前的向量v_k，得到下一个向量v_{k+1}
        #根据幂迭代法的原理，通过不断地将矩阵应用于向量，可以逐渐增强与最大特征值对应的特征向量的分量，从而使得迭代过程收敛到该特征向量
        next_vector = np.dot(M, vector) #矩阵向量乘法,np.dot(M, vector)计算矩阵M与向量vector的乘积，得到新的向量next_vector,也可以使用M.dot(vector)

        #归一化（normalization）是为了确保向量的长度为1，这有助于防止数值溢出或下溢，并保持迭代过程的稳定性
        #保持向量长度为1: v_{k+1} = v_{k+1} / ||v_{k+1}|| - 通过将向量v_{k+1}除以其范数（长度），可以确保向量的长度为1，从而防止数值溢出或下溢
        if np.linalg.norm(next_vector) == 0:
            break #防止除以零的情况发生
        next_vector = next_vector / np.linalg.norm(next_vector) #归一化,np.linalg.norm(next_vector)计算向量next_vector的范数（长度），然后将向量除以其范数以实现归一化

        #估计特征值: λ_k = v_k^T * M * v_k - 通过计算当前向量v_k与矩阵M作用后的向量的内积，可以得到对特征值的估计
        #因为我们的向量已经是归一化的，所以这个估计实际上是对特征值的近似
        #原来估计特征值（rayleigh-quotient）的方法是λ_k = (v_k^T * M * v_k) / (v_k^T * v_k)，但由于v_k已经归一化，分母为1，因此简化为λ_k = v_k^T * M * v_k
        #np.dot(vector.T, np.dot(M, vector))计算当前向量vector与矩阵M作用后的向量的内积，得到对特征值的估计
        #这里是使用当前的unit vector来估计特征值
        rayleigh_quotient = np.dot(vector.T, np.dot(M, vector))

        #计算残差: r_k = ||M * v_k - λ_k * v_k|| - 通过计算矩阵M作用后的向量与估计的特征值乘以当前向量之间的差的范数，可以得到残差
        #残差用于衡量当前估计的特征向量与实际特征向量之间的差距，从而判断迭代是否收敛
        #np.dot(M, vector)计算矩阵M作用后的向量，rayleigh_quotient * vector计算估计的特征值乘以当前向量，两者之差的范数
        diff_vector = np.dot(M, vector) - rayleigh_quotient * vector
        residual = np.linalg.norm(diff_vector) #计算残差,np.linalg.norm(diff_vector)计算向量diff_vector的范数（长度），得到残差值
        residuals.append(residual)#将当前残差添加到残差列表中，以便后续分析迭代过程的收敛性
        vector = next_vector #更新当前向量为下一个向量，进行下一次迭代

    return vector, residuals


####################################################################################################
# Exercise 2: Eigenfaces

def load_images(path: str, file_ending: str=".png") -> (list, int, int):
    """
    Load all images in path with matplotlib that have given file_ending

    Arguments:
    path: path of directory containing image files that can be assumed to have all the same dimensions
    file_ending: string that image files have to end with, if not->ignore file

    Return:
    images: list of images (each image as numpy.ndarray and dtype=float64)
    dimension_x: size of images in x direction
    dimension_y: size of images in y direction
    """

    images = []

    # TODO read each image in path as numpy.ndarray and append to images
    # Useful functions: lib.list_directory(), matplotlib.image.imread(), numpy.asarray()
    file_list = lib.list_directory(path) #列出目录中的所有文件,返回文件名列表

    #按照数值顺序排序文件列表
    # 题目要求 "01_02.png" 在 "01_03.png" 之前。
    # 我们定义一个辅助函数，提取文件名中的所有数字进行排序。
    def extract_numbers(filename):
        nums = [] #用于存储提取的数字
        current_num= '' #用于构建当前数字的字符串
        for char in filename:
            if char.isdigit(): #检查字符是否为数字
                current_num +=char #如果是数字，则将其添加到当前数字字符串中
            else:
                if current_num: #如果当前数字字符串不为空
                    nums.append(int(current_num)) #将当前数字字符串转换为整数并添加到列表中
                    current_num= '' #重置当前数字字符串
        if current_num: #处理文件名结尾的数字
            nums.append(int(current_num))
        return nums
    file_list.sort(key=extract_numbers) #使用自定义的提取数字函数进行排序
    #处理路径分隔符
    if not path.endswith('/'):
        path += '/'#确保路径以斜杠结尾，方便后续拼接文件名

    #遍历文件列表，加载符合条件的图像文件
    for file_name in file_list:
        if file_name.endswith(file_ending): #检查文件名是否以指定的文件结尾
            img = mpl.image.imread(path + file_name) #使用matplotlib加载图像文件
            img_array = np.asarray(img, dtype=np.float64) #将图像转换为numpy数组，数据类型为float64
            images.append(img_array) #将图像数组添加到图像列表中

    # TODO set dimensions according to first image in images
    dimension_y = 0
    dimension_x = 0

    if len(images) > 0:
        dimension_y= images[0].shape[0] #图像的高度（行数）
        dimension_x= images[0].shape[1] #图像的宽度（列数）

    return images, dimension_x, dimension_y


def setup_data_matrix(images: list) -> np.ndarray:
    """
    Create data matrix out of list of 2D data sets.

    Arguments:
    images: list of 2D images (assumed to be all homogeneous of the same size and type np.ndarray)

    Return:
    D: data matrix that contains the flattened images as rows
    """
    # TODO: initialize data matrix with proper size and data type
    if not images:#检查图像列表是否为空
        return np.zeros((0, 0))  # 返回一个空矩阵，如果图像列表为空
    num_images = len(images)  # 图像的数量
    flattened_size = images[0].size #图像的大小（像素总数）,假设所有图像具有相同的尺寸,使用第一个图像的大小作为参考
    D = np.zeros((num_images, flattened_size), dtype=np.float64)  # 初始化数据矩阵

    # TODO: add flattened images to data matrix
    #对应skript 5.1节，将图像矩阵‘线性化’为一维向量，并将其作为数据矩阵D的行
    for i, img in enumerate(images):
        D[i, :] = img.flatten()  # 将图像展平为一维向量，并添加到数据矩阵D的对应行中 


    return D


def calculate_pca(D: np.ndarray) -> (np.ndarray, np.ndarray, np.ndarray):
    """
    Perform principal component analysis for given data matrix.

    Arguments:
    D: data matrix of size m x n where m is the number of observations and n the number of variables

    Return:
    pcs: matrix containing principal components as rows
    svals: singular values associated with principle components
    mean_data: mean that was subtracted from data
    """

    # TODO: subtract mean from data / center data at origin
    #对应skript 5.2.2， 计算数据的重心b，并进行中心化处理
    #mean_data是数据矩阵D的每一列的均值，表示每个变量的平均值，是所有图像的平均图像
    mean_data = np.mean(D, axis=0)  # 计算每一列的均值
    D_centered = D - mean_data  # 从数据矩阵D中减去均值，进行中心化处理

    # TODO: compute left and right singular vectors and singular values
    # Useful functions: numpy.linalg.svd(..., full_matrices=False)
    #对应skript 5.3节，使用奇异值分解（SVD）来计算主成分
    # D = U * S * V^T
    #full_matrices=False参数确保U和V的形状适合于非方阵的情况
    # np.linalg.svd返回U、svals和Vt，其中svals是奇异值的向量形式,第三个参数已经是转置后的V矩阵
    # V^T的行对应于主成分
    U, svals, Vt = np.linalg.svd(D_centered, full_matrices=False)

    pcs = Vt  # 主成分矩阵，Vt的行对应于主成分

    return pcs, svals, mean_data


def accumulated_energy(singular_values: np.ndarray, threshold: float = 0.8) -> int:
    """
    Compute index k so that threshold percent of magnitude of singular values is contained in
    first k singular vectors.

    Arguments:
    singular_values: vector containing singular values
    threshold: threshold for determining k (default = 0.8)

    Return:
    k: threshold index
    """

    # TODO: Normalize singular value magnitudes
    #题目中的图表显示‘accumulated singular values’，实际上是指奇异值的累积和占总和的比例,而非平方和
    #计算奇异值的总和
    total_magnitude = np.sum(singular_values) # np.sun()计算奇异值的总和
    k = 0
    if total_magnitude == 0:
        return 0  # 防止除以零的情况发生
    # TODO: Determine k that first k singular values make up threshold percent of magnitude
    #计算累积奇异值的和，直到达到指定的阈值比例
    #找到第一个累积占比达到或超过threshold的索引的位置
    #np.argmax返回第一个true值的索引，索引从0开始，k代表个数，所以需要加1
    accumulated_magnitude = np.cumsum(singular_values)  # 计算奇异值的累积和
    k = np.argmax(accumulated_magnitude/total_magnitude >= threshold) + 1  # 找到第一个累积占比达到或超过threshold的索引位置
    return int(k)
    

def project_faces(pcs: np.ndarray, images: list, mean_data: np.ndarray) -> np.ndarray:
    """
    Project given image set into basis.

    Arguments:
    pcs:  matrix containing principal components / eigenfunctions as rows
    images: original input images from which pcs were created
    mean_data: mean data that was subtracted before computation of SVD/PCA

    Return:
    coefficients: basis function coefficients for input images, each row contains coefficients of one image
    """

    # TODO: initialize coefficients array with proper size
    if not images:
        return np.array([])  # 返回一个空数组，如果图像列表为空
    num_images =len(images)  # 图像的数量
    num_pcs = pcs.shape[0]  # 主成分的数量
    coefficients = np.zeros((num_images, num_pcs))  # 初始化系数矩阵,每行对应一张图像的系数

    # TODO: iterate over images and project each normalized image into principal component basis
    # 对应skript 5.1 Eq 5.5: x = c^T(g - b)
    # 这里g是图像，b是均值图像，c是主成分矩阵，C^T是特征向量矩阵的转置（或者说这里pcs的行已经是基向量）
    #投影系数 =  主成分矩阵 * (图像 - 均值图像)
    for i, img in enumerate(images):
        img_vector= img.flatten()  # 将图像展平为一维向量
        #中心化
        normalized_img= img_vector- mean_data  # 减去均值图像，进行归一化处理
        #使用矩阵向量乘法计算投影系数，公式为 coefficients = pcs * normalized_img
        coefficients[i, :] = np.dot(pcs, normalized_img)  # 计算投影系数，并存储在系数矩阵中

    return coefficients


def identify_faces(coeffs_train: np.ndarray, pcs: np.ndarray, mean_data: np.ndarray, path_test: str) -> (
np.ndarray, list, np.ndarray):
    """
    Perform face recognition for test images assumed to contain faces.

    For each image coefficients in the test data set the closest match in the training data set is calculated.
    The distance between images is given by the angle between their coefficient vectors.

    Arguments:
    coeffs_train: coefficients for training images, each image is represented in a row
    path_test: path to test image data

    Return:
    scores: Matrix with correlation between all train and test images, train images in rows, test images in columns
    imgs_test: list of test images
    coeffs_test: Eigenface coefficient of test images
    """

    # TODO: load test data set
    #使用之前实现的load_images函数加载测试图像
    imgs_test, _, _ = load_images(path_test)

    # TODO: project test data set into eigenbasis
    #使用之前实现的project_faces函数将测试图像投影到主成分空间
    coeffs_test = project_faces(pcs, imgs_test, mean_data)


    # TODO: Initialize scores matrix with proper size
    num_train = coeffs_train.shape[0]  # 训练图像的数量
    num_test = coeffs_test.shape[0]  # 测试图像的数量
    scores = np.zeros((num_train, num_test))  # 初始化分数矩阵
    # TODO: Iterate over all images and calculate pairwise correlation
    #题目要求：Als Ähnlichkeitsmaß soll der Winkel zwischen den Bildern dienen (角度作为相似度度量)
    #Cosine Similarity 余弦相似度: cos(theta) = (A · B) / (||A|| * ||B||)
    #Angle θ = arccos( (A · B) / (||A|| * ||B||) )
    for i in range(num_train):
        vector_train = coeffs_train[i, :]  # 训练图像的系数向量
        norm_train = np.linalg.norm(vector_train)  # 训练图像系数向量的范数
        for j in range(num_test):
            vector_test = coeffs_test[j, :]  # 测试图像的系数向量
            norm_test = np.linalg.norm(vector_test)  # 测试图像系数向量的范数
            if norm_train == 0 or norm_test == 0:
                scores[i, j] = np.pi / 2  # 如果任一向量的范数为零，设定角度为90度（π/2弧度）
            else:
                dot_product = np.dot(vector_train, vector_test)  # 计算点积
                cosine_similarity = dot_product / (norm_train * norm_test)  # 计算余弦相似度
                #确保余弦值在[-1, 1]范围内，防止数值误差导致arccos出错
                cosine_similarity = np.clip(cosine_similarity, -1.0, 1.0)
                angle = np.arccos(cosine_similarity)  # 计算角度
                scores[i, j] = angle  # 将角度存储在分数矩阵中

    return scores, imgs_test, coeffs_test


if __name__ == '__main__':

    A = np.random.randn( 7, 7)
    A = A.transpose().dot(A)
    L,U = np.linalg.eig( A)
    L[1] = L[0] - 10**-3
    A = U.dot(np.diag(L)).dot(U.transpose())
    print( )
    np.set_printoptions(precision=16)
    print( A.flatten())

    A = np.array( [ 18.2112344794043359,   0.7559886314903312,  7.2437569750169502,
                    -13.8991061752623271,   4.8768689715057691,  -1.318055436971276,
                    -6.7829844205260148,   0.7559886314903312,   7.9204801042364448,
                     1.5378938590357767,   7.1775560914639325,   2.8536549530686015,
                     1.9998683983340397,  -5.9532930598376685,   7.2437569750169502,
                     1.5378938590357767,   9.841906218619128,   0.5841092845624152,
                     6.7510103134860797,   4.6111951240722888,  -8.9825300821798191,
                    -13.8991061752623271,   7.1775560914639334,   0.5841092845624152,
                     24.2028041177043818,   0.8180957104689988,   6.6087248591945729,
                    -4.1573996873552073,   4.8768689715057691,   2.8536549530686015,
                     6.7510103134860806,   0.8180957104689979,   7.0366782892027206,
                     5.4944303652858073,  -9.0773671527609796,  -1.318055436971276,
                     1.9998683983340397,   4.6111951240722888,   6.608724859194572,
                     5.4944303652858073,   8.1889694453300805,  -7.1176432086570651,
                    -6.7829844205260148,  -5.9532930598376685,  -8.9825300821798191,
                    -4.1573996873552046,  -9.0773671527609796,  -7.1176432086570633,
                    13.664209790087753 ])
    A = A.reshape( (7,7))

    ev, res = power_iteration( A)



    print( 'ev = ' + str(ev))

    print("All requested functions for the assignment have to be implemented in this file and uploaded to the "
          "server for the grading.\nTo test your implemented functions you can "
          "implement/run tests in the file tests.py (> python3 -v test.py [Tests.<test_function>]).")
