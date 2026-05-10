import numpy as np

####################################################################################################
# Exercise 1: DFT

# ================================================================================================
# dft_matrix: 构造离散傅里叶变换(DFT)矩阵
# 
# 【原理】
# DFT将时域信号转换到频域。对于长度为n的信号，DFT矩阵F的元素为 F[j,k] = omega^(j*k)
# 其中 omega = e^(-2πi/n) 是n次单位根，也叫旋转因子(twiddle factor)
#
# 【做了什么】
# 构造一个n×n的复数矩阵，每个元素是omega的幂次，然后归一化使其成为正交矩阵
#
# 【为什么这么做】
# 用矩阵形式可以直接通过 F @ signal 计算DFT，概念清晰，便于理解DFT的本质
# 归一化因子1/sqrt(n)使得DFT矩阵成为酉矩阵，满足 F* @ F = I
#
# 【为什么不用其他方法】
# 可以用numpy.fft但题目禁止了；也可以直接用求和公式但矩阵形式更直观
# ================================================================================================
def dft_matrix(n: int) -> np.ndarray:
    """
    Construct DFT matrix of size n. # 构建n阶DFT矩阵

    Arguments: 
    n: size of DFT matrix # 矩阵大小

    Return:
    F: DFT matrix of size n # 返回n阶DFT矩阵

    Forbidden:
    - numpy.fft.*
    """
    # TODO: initialize matrix with proper size
    F = np.zeros((n,n), dtype='complex128')  # 创建n×n的复数矩阵，初始化为0，dtype指定为128位复数

    # TODO: create principal term for DFT matrix
    omega=np.exp(-2j* np.pi/n)  # 计算n次单位根 ω = e^(-2πi/n)，-2j表示-2i（虚数单位）
    
    # TODO: fill matrix with values
    for j in range(n):  # 遍历行
        for k in range(n):  # 遍历列
            F[j,k] = omega **(j*k)  # F[j,k] = ω^(j*k)，这是DFT矩阵的定义公式
            
    # TODO: normalize dft matrix
    F=F /np.sqrt(n)  # 归一化：除以√n，使DFT矩阵成为酉矩阵

    return F


# ================================================================================================
# is_unitary: 检验矩阵是否为酉矩阵(unitary matrix)
#
# 【原理】
# 酉矩阵满足 F* @ F = I，其中F*是共轭转置(Hermitian transpose)，I是单位矩阵
# 共轭转置 = 先转置再取复共轭，numpy里就是 np.conjugate(matrix.T)
#
# 【做了什么】
# 计算 F* @ F，然后用np.allclose检查是否接近单位矩阵（考虑浮点误差）
#
# 【为什么这么做】
# 直接按定义来验证，计算共轭转置与原矩阵相乘，看结果是否为单位阵
#
# 【注意】
# 一开始我只写了 np.conjugate(matrix) 忘了转置.T，这是个常见错误！
# 共轭和共轭转置是两回事
# ================================================================================================
def is_unitary(matrix: np.ndarray) -> bool:
    """
    Check if the passed in matrix of size (n times n) is unitary.

    Arguments:
    matrix: the matrix which is checked

    Return:
    unitary: True if the matrix is unitary
    """
    unitary = False  # 默认设为False，只有验证通过才改为True
    # TODO: check that F is unitary, if not return false
    # F* @ F should equal identity (F* is conjugate transpose)
    U = np.conjugate(matrix.T) @ matrix  # 计算F* @ F，conjugate取共轭，.T转置，@矩阵乘法
    if U.shape[0] == U.shape[1] and np.allclose(U,np.eye(U.shape[0])):  # allclose检查是否近似相等（考虑浮点误差），eye生成单位矩阵
        unitary = True  # 如果F* @ F ≈ I，则是酉矩阵
    return unitary


# ================================================================================================
# create_harmonics: 创建δ冲激信号并计算其DFT
#
# 【原理】
# δ冲激信号 e_i 只有第i个位置是1，其他都是0
# 对e_i做DFT相当于提取DFT矩阵的第i列，这一列就是对应的谐波(harmonic)
#
# 【做了什么】
# 创建n个δ冲激信号，每个信号的"1"在不同位置
# 对每个信号用DFT矩阵做变换，得到对应的频域表示
#
# 【为什么这么做】
# 通过观察不同位置δ冲激的DFT结果，可以直观理解DFT矩阵每一列的物理意义
# 这些列就是构成任意信号的基本谐波分量
# ================================================================================================
def create_harmonics(n: int = 128) -> (list, list):
    """
    Create delta impulse signals and perform the fourier transform on each signal.

    Arguments:
    n: the length of each signal

    Return:
    sigs: list of np.ndarrays that store the delta impulse signals
    fsigs: list of np.ndarrays with the fourier transforms of the signals
    """

    # list to store input signals to DFT
    sigs = []  # 存储输入的δ冲激信号
    # Fourier-transformed signals
    fsigs = []  # 存储傅里叶变换后的信号

    # TODO: create signals and extract harmonics out of DFT matrix
    F=dft_matrix(n)  # 先构造DFT矩阵，后面用它来做变换
    
    for i in range(n):  # 创建n个δ冲激信号
        impl = np.zeros(n)  # 初始化全0数组
        impl[i]=1  # 第i个位置设为1，形成δ冲激 e_i = (0,...,1,...,0)
        sigs.append(impl)  # 把这个冲激信号加入列表
        
        fsig = F@impl  # 用DFT矩阵乘以冲激信号，得到其频域表示（实际上就是F的第i列）
        fsigs.append(fsig)  # 把变换结果加入列表
        
    return sigs, fsigs


####################################################################################################
# Exercise 2: FFT

# ================================================================================================
# shuffle_bit_reversed_order: 按位逆序重排数组元素
#
# 【原理】
# Cooley-Tukey FFT算法需要先把输入数据按位逆序排列
# 比如对于n=8, 索引3的二进制是011，反转后是110=6，所以data[3]和data[6]要交换位置
#
# 【做了什么】
# 对每个索引i，计算它的位反转索引reversed_index，然后把data[i]放到新位置
#
# 【为什么这么做】
# FFT的蝴蝶运算要求数据按特定顺序排列。位反转排序使得后续的蝴蝶操作可以
# 就地(in-place)进行，相邻的元素正好是需要合并的子问题的结果
#
# 【实现细节】
# 用位运算：左移<<，右移>>，与运算&来逐位反转
# 这里用新数组存结果，也可以原地交换但要注意只交换一次
# ================================================================================================
def shuffle_bit_reversed_order(data: np.ndarray) -> np.ndarray:
    """
    Shuffle elements of data using bit reversal of list index.

    Arguments:
    data: data to be transformed (shape=(n,), dtype='float64')

    Return:
    data: shuffled data array
    """

    # TODO: implement shuffling by reversing index bits
    n = data.shape[0]  # 获取数组长度
    num_bits = int(np.log2(n))  # 计算需要多少位来表示索引，比如n=8需要3位(000~111)
    shuffled_data = np.zeros_like(data, dtype='complex128')  # 创建同样大小的新数组存结果

    for i in range(n):  # 遍历每个索引
        reversed_index = 0  # 初始化反转后的索引
        for j in range(num_bits):  # 逐位处理
            reversed_index = reversed_index << 1  # 左移一位，给新的bit腾位置
            current_bit = (i >> j) & 1  # 取i的第j位：右移j位后与1做与运算
            reversed_index += current_bit  # 把这个bit加到reversed_index的最低位
        
        shuffled_data[reversed_index] = data[i]  # 把data[i]放到反转后的位置
    
    return shuffled_data


# ================================================================================================
# fft: 快速傅里叶变换 (Cooley-Tukey算法)
#
# 【原理】
# FFT利用DFT的对称性，把O(n²)的计算降到O(n log n)
# 核心思想：长度为n的DFT可以分解为两个长度为n/2的DFT，然后用蝴蝶运算合并
#
# 【算法步骤】
# 1. 位反转重排：把数据按bit-reversed顺序排列
# 2. 蝴蝶运算：从底向上合并，每层处理2^m个元素的子问题
#    - m=0时，相邻2个元素合并
#    - m=1时，相邻4个元素合并
#    - 依此类推，直到合并整个数组
# 3. 归一化：除以sqrt(n)
#
# 【蝴蝶运算公式】
# p = omega * fdata[j]
# fdata[j] = fdata[i] - p
# fdata[i] = fdata[i] + p
# 其中 omega = e^(-2πik/2^(m+1)) 是旋转因子
#
# 【为什么不用递归】
# 递归版本更直观但有函数调用开销，迭代版本用while循环更高效
# 而且迭代版本可以原地计算，不需要额外空间
# ================================================================================================
def fft(data: np.ndarray) -> np.ndarray:
    """
    Perform real-valued discrete Fourier transform of data using fast Fourier transform.

    Arguments:
    data: data to be transformed (shape=(n,), dtype='float64')

    Return:
    fdata: Fourier transformed data

    Note:
    This is not an optimized implementation but one to demonstrate the essential ideas
    of the fast Fourier transform.

    Forbidden:
    - numpy.fft.*
    """

    fdata = np.asarray(data, dtype='complex128')  # 把输入转成复数数组，asarray不会复制如果已经是正确类型
    n = fdata.size  # 获取数据长度

    # check if input length is power of two
    if not n > 0 or (n & (n - 1)) != 0:  # n&(n-1)==0是判断2的幂次的技巧，比如8=1000，7=0111，8&7=0
        raise ValueError  # 如果不是2的幂次就报错，因为Cooley-Tukey FFT要求长度是2^k

    # TODO: first step of FFT: shuffle data
    fdata = shuffle_bit_reversed_order(fdata)  # 第一步：位反转重排，直接对fdata操作

    # TODO: second step, recursively merge transforms
    m = 1  # m表示当前处理的子问题大小，从1开始（最底层）
    while m<n:  # 从底向上，每次m翻倍，直到m=n
        for k in range(m):  # k是蝴蝶运算中的频率索引，范围[0, m)
            omega = np.exp(-2j * np.pi * k / (2*m))  # 计算旋转因子 ω = e^(-2πik/2m)
            for i in range(k,n,2*m):  # i从k开始，每次跳2m，遍历所有需要做蝴蝶运算的位置
                j = i+m  # j是与i配对的元素位置，距离为m
                temp = omega*fdata[j]  # 计算 ω * fdata[j]，这是蝴蝶运算的关键
                fdata[j] = fdata[i]-temp  # 蝴蝶运算：下半部分 = 上-temp
                fdata[i] = fdata[i]+temp  # 蝴蝶运算：上半部分 = 上+temp
        m *= 2  # 进入下一层，子问题大小翻倍

    # TODO: normalize fft signal
    fdata /=np.sqrt(n)  # 归一化，除以√n，与DFT矩阵的归一化一致
    
    return fdata


# ================================================================================================
# generate_tone: 生成指定频率的正弦波音调
#
# 【原理】
# 声音是空气振动，单一频率的振动就是正弦波 sin(2πft)
# 中央C的频率是261.626 Hz，采样率44100是CD音质标准
#
# 【做了什么】
# 在[0,1)秒的时间范围内，按采样率生成采样点，计算每个点的正弦值
#
# 【为什么用endpoint=False】
# 题目要求采样区间是[0,1)，不包含右端点
# 如果包含endpoint，会采样到t=1.0，周期信号会有重复点
#
# 【为什么用sin不用cos】
# 两者只差一个相位，对于听觉来说没区别，但习惯上用sin
# ================================================================================================
def generate_tone(f: float = 261.626, num_samples: int = 44100) -> np.ndarray:
    """
    Generate tone of length 1s with frequency f (default mid C: f = 261.626 Hz) and return the signal.

    Arguments:
    f: frequency of the tone

    Return:
    data: the generated signal
    """

    # sampling range
    x_min = 0.0  # 采样起点，0秒
    x_max = 1.0  # 采样终点，1秒（但不包含）

    data = np.zeros(num_samples)  # 初始化结果数组

    # TODO: Generate sine wave with proper frequency
    t = np.linspace(x_min, x_max, num_samples, endpoint=False)  # 生成[0,1)区间的num_samples个等间距点，endpoint=False不包含右端点
    data = np.sin(2*np.pi*f*t)  # 计算正弦波：sin(2πft)，f是频率，t是时间点

    return data


# ================================================================================================
# low_pass_filter: 低通滤波器，滤除高频成分
#
# 【原理】
# 低通滤波保留低频，去除高频。在频域里很简单：把高频分量直接设为0
# 由于实数信号的FFT结果有共轭对称性，频率分布是：
# [0, 1, 2, ..., n/2-1, n/2, -(n/2-1), ..., -2, -1] * (采样率/n)
# 所以高频在数组的中间部分
#
# 【做了什么】
# 1. FFT变换到频域
# 2. 把中间的高频部分(bandlimit到n-bandlimit)设为0
# 3. IFFT变回时域
#
# 【IFFT怎么算】
# 用共轭技巧：IFFT(X) = conj(FFT(conj(X)))
# 因为题目禁用numpy.fft，所以用这个数学恒等式来实现逆变换
#
# 【为什么用for循环设零】
# 也可以用切片 fdata[bandlimit_index:-bandlimit_index] = 0
# 但for循环更清楚地表达了"中间部分设为0"的逻辑，不容易搞错边界
# ================================================================================================
def low_pass_filter(adata: np.ndarray, bandlimit: int = 1000, sampling_rate: int = 44100) -> np.ndarray:
    """
    Filter high frequencies above bandlimit.

    Arguments:
    adata: data to be filtered
    bandlimit: bandlimit in Hz above which to cut off frequencies
    sampling_rate: sampling rate in samples/second

    Return:
    adata_filtered: filtered data
    """
    
    # translate bandlimit from Hz to dataindex according to sampling rate and data size
    bandlimit_index = int(bandlimit*adata.size/sampling_rate)  # 把Hz转换为数组索引：索引 = 频率 * 数据长度 / 采样率

    # TODO: compute Fourier transform of input data
    fdata = fft(adata)  # 对输入信号做FFT，转到频域

    # TODO: set high frequencies above bandlimit to zero, make sure the almost symmetry of the transform is respected.
    for i in range(len(fdata)):  # 遍历所有频率分量
        if i > bandlimit_index and i < len(fdata) - bandlimit_index:  # 如果在中间的高频区域（考虑对称性）
            fdata[i] = 0  # 把高频分量设为0

    # TODO: compute inverse transform and extract real component
    # inverse fft using conjugate trick
    adata_filtered = np.conj(fft(np.conj(fdata)))  # IFFT技巧：IFFT(X) = conj(FFT(conj(X)))，先共轭再FFT再共轭
    adata_filtered = adata_filtered.real  # 取实部，因为原信号是实数，虚部应该接近0
    
    return adata_filtered


if __name__ == '__main__':
    print("All requested functions for the assignment have to be implemented in this file and uploaded to the "
          "server for the grading.\nTo test your implemented functions you can "
          "implement/run tests in the file tests.py (> python3 -v test.py [Tests.<test_function>]).")
