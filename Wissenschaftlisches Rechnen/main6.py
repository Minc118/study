import numpy as np
from tqdm import tqdm
from lib import *

class LinearModel(Model):
    """
    A simple linear model with weights (bias is implicit).

    Attributes:
        _w (np.ndarray): The weights of the model, initialized with a normal distribution.
        _grad (np.ndarray): Stores the gradient w.r.t. the weights after the forward pass.
    """

    def __init__(self, in_features: int):
        """
        Initializes the LinearModel with random weights.

        Args:
            in_features (int): The number of input features (dimension of the input vectors).
        """

        self._w = np.random.normal(0, 0.01, size=(in_features,))
        self._grad = None

    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Performs the forward pass of the linear model.

        Args:
            x (np.ndarray): The input data vectors of shape (n_samples, n_features).

        Returns:
            np.ndarray: The scalar results of the forward pass

        Forbidden:
            numpy.gradient, numpy.diff
        """

        # TODO: Implement the forward pass 
        # TODO: Compute the gradient and store it in self._grad
        
        # ===================== 任务1: 线性模型的前向传播 (0.5分) =====================
        # 【概括】
        # 这里需要实现线性模型的前向传播，即计算 y = X @ w
        # 其中 X 是输入数据矩阵 (n_samples, n_features)，w 是权重向量
        # 同时需要存储梯度 ∂y/∂w = x，因为 y = w^T * x，对 w 求导得到 x
        # 这个梯度会在 backward() 中返回，用于后续的链式法则计算
        # ========================================================================
        
        Result = x @ self._w  # 矩阵乘法，计算每个样本的预测值 y = X @ w
        self._grad = x        # 存储输入作为梯度，因为 ∂y/∂w = x
        return Result         # 返回预测结果，形状为 (n_samples,)
    
    def backward(self) -> np.ndarray:
        """
        Performs the backward pass to retrieve the gradient for the last input.
        
        Args:
            None

        Returns:
            np.ndarray: The gradients.

        Forbidden:
            numpy.gradient, numpy.diff
        """

        # TODO: Implement the backward pass that returns the gradient 
        return self._grad  # 返回在forward中存储的梯度 ∂y/∂w = x
    
class L2Loss(Loss):
    """
    Computes the L2Loss between the target values and the predictions.
    
    Attributes:
        _grad (np.ndarray): The gradient of the loss with respect to the inputs.
    """

    def forward(self, t: np.ndarray, y: np.ndarray) -> np.float64:
        """
        Computes the L2 loss value and caches the gradient.

        Args:
            t (np.ndarray): Target values.
            y (np.ndarray): Predicted values.

        Returns:
            np.float64: The computed loss.

        Forbidden:
            numpy.gradient, numpy.diff
        """

        # TODO: Implement L2Loss forward
        
        # ===================== 任务2.1: L2损失函数 (0.5分) =====================
        # 【概括】
        # L2损失是最小二乘损失，公式为: L = (1/n) * Σ(t_i - y_i)²
        # 这个损失函数惩罚预测值与真实值的平方差
        # 梯度推导: ∂L/∂y = ∂[(t-y)²]/∂y = -2(t-y) = 2(y-t)
        # 由于是平均值，所以还要除以样本数n: ∂L/∂y = (2/n)(y-t)
        # ====================================================================
        
        N = len(t)                      # 获取样本数量
        Loss_val = np.mean((t-y)**2)    # 计算平均平方误差: (1/n)*Σ(t-y)²
        self._grad = 2/N * (y-t)        # 计算梯度: (2/n)*(y-t)
        return Loss_val                 # 返回损失值
    
    def backward(self) -> np.ndarray:
        """
        Returns the gradient of the loss with respect to the last inputs.

        Returns:
            np.ndarray: The computed gradient.

        Forbidden:
            numpy.gradient, numpy.diff
        """

        # TODO: Implement L2Loss backward
        return self._grad  # 返回在forward中计算的梯度 ∂L/∂y

class PerceptronLoss(Loss):
    """
    Computes the Perceptron loss between the target values and the predictions.
    
    Attributes:
        _grad (np.ndarray): The gradient of the loss with respect to the inputs.
    """

    def forward(self, t: np.ndarray, y: np.ndarray) -> np.float64:
        """
        Computes the Perceptron Loss value and caches the gradient.

        Args:
            t (np.ndarray): Target values.
            y (np.ndarray): Predicted values.

        Returns:
            np.float64: The computed loss.

        Forbidden:
            numpy.gradient, numpy.diff
        """

        # TODO: Implement PerceptronLoss forward
        
        # ===================== 任务2.2: 感知机损失函数 (0.5分) =====================
        # 【概括】
        # 感知机损失公式: ℓ_P(t, y) = max(0, -t*y)
        # 只惩罚错误分类的点（当 t 和 y 符号不同时，t*y < 0，损失 > 0）
        # 当分类正确时（t*y > 0），损失为 0
        # 梯度: 当 t*y < 0 时，∂ℓ/∂y = -t；否则为 0
        # 由于是平均值，梯度要除以n: ∂L/∂y = -t/n (当ty<0时)
        # ======================================================================
        
        sample_Num = len(t)                           # 获取样本数量
        loss_Value = np.mean(np.maximum(0, -t*y))     # 计算平均损失: (1/n)*Σmax(0,-ty)
        self._grad = np.where(t*y < 0, -t/sample_Num, 0)  # 梯度: 错误分类时为-t/n，否则为0
        return loss_Value                             # 返回损失值
    
    def backward(self) -> np.ndarray:
        """
        Returns the gradient of the loss with respect to the last input.

        Returns:
            np.ndarray: The computed gradient.

        Forbidden:
            numpy.gradient, numpy.diff
        """

        # TODO: Implement PerceptronLoss backward
        return self._grad  # 返回在forward中计算的梯度 ∂L/∂y

class HingeLoss(Loss):
    """
    Computes the Hinge loss between the target values and the predictions.
    
    Attributes:
        _grad (np.ndarray): The gradient of the loss with respect to the input
    """

    def forward(self, t: np.ndarray, y: np.ndarray) -> np.float64:
        """
        Computes the Hinge loss value and caches the gradient.

        Args:
            t (np.ndarray): Target values.
            y (np.ndarray): Predicted values.

        Returns:
            np.float64: The computed loss.

        Forbidden:
            numpy.gradient, numpy.diff
        """

        # TODO: Implement HingeLoss forward
        
        # ===================== 任务2.3: 铰链损失函数 (0.5分) =====================
        # 【概括】
        # 铰链损失公式: ℓ_H(t, y) = max(0, 1 - t*y)
        # 不仅要求分类正确，还要求有一定的「安全边距」(margin)
        # 只有当 t*y >= 1（足够确信地正确分类）时，损失才为 0
        # 梯度: 当 t*y < 1 时，∂ℓ/∂y = -t；否则为 0
        # 由于是平均值，梯度要除以n: ∂L/∂y = -t/n (当ty<1时)
        # ======================================================================
        
        Num_samples = len(t)                          # 获取样本数量
        hinge_Loss = np.mean(np.maximum(0, 1-t*y))    # 计算平均损失: (1/n)*Σmax(0,1-ty)
        self._grad = np.where(t*y<1, -t/Num_samples, 0)  # 梯度: ty<1时为-t/n，否则为0
        return hinge_Loss                             # 返回损失值
    
    def backward(self) -> np.ndarray:
        """
        Returns the gradient of the loss with respect to the last input.

        Returns:
            np.ndarray: The computed gradient.

        Forbidden:
            numpy.gradient, numpy.diff
        """

        # TODO: Implement HingeLoss backward
        return self._grad  # 返回在forward中计算的梯度 ∂L/∂y

def training_loop(
        model: Model, 
        X_train: np.ndarray, 
        t_train: np.ndarray,
        loss_fn: Loss,
        num_epochs: int = 30, 
        batch_size: int = 100, 
        step_size: float = 0.01,
        progress_bar: tqdm = None,
    ) -> Model:
    """
    Performs gradient descent on the model.

    Args:
        model (Model): The model on which gradient descent should be performed.
        X_train (np.ndarray): The training features.
        t_train (np.ndarray): The training labels.
        loss_fn (Loss): The loss function for the loss calculation.
        num_epochs (int): Number of epochs for which the model is trained.
        batch_size (int): Size of the batches.
        step_size (float): The step size of the gradient descent step.
        progress_bar (tqdm): Used to show the current training progress with a progress bar.

    Returns:
        Model: The trained model.
    """

    # n: number of data points
    # d: dimensionality of the data points
    n, d = X_train.shape

    for e in range(num_epochs):
        p = np.random.permutation(n)
        X_p = X_train[p]
        t_p = t_train[p]

        # update Progress Bar
        if  progress_bar is not None:
             progress_bar.update(1) 

        for batch in range(int(np.ceil(n/batch_size))):
            batch_start = batch * batch_size
            batch_end = min((batch+1) * batch_size, n)
            X_b = X_p[batch_start:batch_end]
            t_b = t_p[batch_start:batch_end]
            
            # TODO: Calculate the gradient of the model and update its parameters with gradient descent
            
            # ===================== 任务3: 梯度下降训练循环 (1.0分) =====================
            # 【概括】
            # 使用链式法则计算总梯度: ∂L/∂w = ∂L/∂y * ∂y/∂w
            # 其中 ∂L/∂y 来自损失函数的 backward()，∂y/∂w 来自模型的 backward()
            # 然后使用梯度下降更新权重: w = w - step_size * gradient
            # 步骤: 1.前向传播 2.计算损失 3.链式法则求梯度 4.更新权重
            # =====================================================================
            
            y_Pred = model.forward(X_b)       # 步骤1: 前向传播，获取预测值 y = X @ w
            loss_fn.forward(t_b, y_Pred)      # 步骤2: 计算损失（同时内部计算梯度）
            
            Loss_grad = loss_fn.backward()   # 步骤3a: 获取损失函数梯度 ∂L/∂y
            Model_grad = model.backward()    # 步骤3b: 获取模型梯度 ∂y/∂w = X
            total_Grad = Loss_grad @ Model_grad  # 步骤3c: 链式法则 ∂L/∂w = ∂L/∂y @ ∂y/∂w
            
            model.update(-step_size * total_Grad)  # 步骤4: 梯度下降更新 w = w - lr * grad

    return model


def prepare_labels(t: np.ndarray, target_digit: int) -> np.ndarray:
    """
    Prepares labels for a one-vs-all training setup.

    All entries in t that correspond to the target digit are encoded as 1,
    while all other entries are encoded as -1.

    Parameters
    ----------
    t : np.ndarray
        Array containing digit labels (0-9).
    target_digit : int
        The digit treated as the positive class.

    Returns
    -------
    np.ndarray
        Array containing labels in {-1, 1}.
    """
    assert target_digit in range(10)

    # ===================== 任务4.1: 准备One-vs-All标签 (0.5分) =====================
    # 【概括】
    # 将多分类问题(0-9十个数字)转换为二分类问题
    # 对于目标数字 target_digit，将其标记为 +1，其他所有数字标记为 -1
    # 这样每个分类器只需要区分「是这个数字」vs「不是这个数字」
    # 输入数组不能被修改，需要返回新数组
    # =========================================================================
    
    Binary_labels = np.where(t==target_digit, 1, -1).astype(np.float64)  # 目标数字=+1, 其他=-1
    return Binary_labels  # 返回转换后的二分类标签

def train_models(
        loss_fn: Loss,
        X_train: np.ndarray,
        t_train: np.ndarray,
        num_epochs: int,
        digits_count: int,
        batch_size: int,
        step_size: float,
        progress_bar: tqdm = None,
    ) -> list:
    """
    Trains one linear model per digit using a one-vs-all strategy.

    For each digit from 0 to 9, a separate LinearModel is created and trained
    to distinguish the current digit (label 1) from all other digits (label -1),
    using the given loss function.

    Parameters
    ----------
    loss_fn : Loss
        The loss function used for training all models.

    Returns
    -------
    list[LinearModel]
        A list of 10 trained linear models, ordered by digit
        (model 0 corresponds to digit 0, model 1 to digit 1, etc.).
    """

    models = []
    
    # TODO: Train one linear model per digit with given loss function. Use the given variables as parameters when calling the training_loop() function.
    # Prepare the labels on the t_train before caling the training_loop().
    
    # ===================== 任务4.2: 训练十个二分类器 (0.5分) =====================
    # 【概括】
    # One-vs-All 策略：为每个数字（0-9）训练一个独立的线性模型
    # 每个模型学习区分「是这个数字」(+1) 和「不是这个数字」(-1)
    # 步骤: 1.创建新模型 2.准备二分类标签 3.调用training_loop训练 4.添加到列表
    # 最终返回10个训练好的模型，按数字顺序排列
    # =========================================================================
    
    Feature_dim = X_train.shape[1]  # 获取特征维度 (784+1=785，包含bias)
    
    for Digit in range(digits_count):  # 遍历每个数字0-9
        new_Model = LinearModel(Feature_dim)        # 步骤1: 创建新的线性模型
        t_Binary = prepare_labels(t_train, Digit)   # 步骤2: 准备二分类标签
        
        # 步骤3: 调用训练循环训练模型
        trained_Model = training_loop(new_Model, X_train, t_Binary, loss_fn,
                         num_epochs, batch_size, step_size, progress_bar)
        models.append(trained_Model)  # 步骤4: 将训练好的模型添加到列表

    return models  # 返回10个训练好的模型


def predict(models: list, X_test: np.ndarray) -> np.ndarray: 
    """
    Performs class prediction for the given test data.

    For each linear model in the list `models`, the model outputs are computed
    for all test samples. 
    (one-vs-all classification).

    Parameters
    ----------
    models : list[LinearModel]
        List of trained linear models, one per class.
    X_test : np.ndarray
        Test data of shape (n_samples, n_features).

    Returns
    -------
    np.ndarray
        Array of length `n_samples` containing the predicted class labels
        (index of the model with the maximum output) for each test sample.
    """
    # TODO: Use the LinearModel's forward() method to compute scores for the test samples.
    # The score represents how confident the model is that the input image depicts the digit it was trained to recognize.
    # Return a NumPy array of predicted digits for each Image in X_test. 
    
    # ===================== 任务4.3: 多分类预测 (1.0分) =====================
    # 【概括】
    # 使用所有10个模型对每个测试样本进行预测
    # 每个模型输出一个「置信度」分数，表示它认为输入是对应数字的程度
    # 最终预测结果是置信度最高的模型对应的数字
    # 步骤: 1.创建分数矩阵 2.每个模型计算分数 3.取最大值索引作为预测
    # ====================================================================
    
    Num_test = X_test.shape[0]                       # 获取测试样本数量
    All_scores = np.zeros((Num_test, len(models)))   # 创建分数矩阵 (样本数, 模型数)
    
    for idx, curr_Model in enumerate(models):        # 遍历每个模型
        All_scores[:, idx] = curr_Model.forward(X_test)  # 计算该模型对所有样本的分数
    
    Predictions = np.argmax(All_scores, axis=1)      # 取每行最大值的索引作为预测数字
    return Predictions  # 返回预测结果数组


if __name__ == "__main__":    
    num_epochs, digits_count, batch_size, step_size = 30, 10, 50, 0.001

    # You can change the data set to the original MNIST (will install from internet)
    X_train, t_train, X_test, t_test = load_dataset('cg-digits')
    modelsList = []
    l2loss = L2Loss()
    ploss = PerceptronLoss()
    hloss = HingeLoss()

    # Train on L2Loss
    with tqdm(total=num_epochs*digits_count, desc=l2loss.__class__.__name__ + "-Training") as progress_bar:
        models = train_models(l2loss, X_train, t_train, num_epochs, digits_count, batch_size, step_size, progress_bar)
    modelsList.append((models, l2loss.__class__.__name__))
    p = predict(models, X_test)
    print(f"L2Loss Accuracy: {100 * (p == t_test).mean()}%")

    # Train on PerceptronLoss
    with tqdm(total=num_epochs*digits_count, desc=ploss.__class__.__name__ + "-Training") as progress_bar:
        models = train_models(ploss, X_train, t_train, num_epochs, digits_count, batch_size, step_size, progress_bar)
    modelsList.append((models, ploss.__class__.__name__))
    p = predict(models, X_test)
    print(f"Perceptron Loss Accuracy: {100 * (p == t_test).mean()}%")

    # Train on HingeLoss
    with tqdm(total=num_epochs * digits_count, desc=hloss.__class__.__name__ + "-Training") as progress_bar:
        models = train_models(hloss,X_train, t_train, num_epochs, digits_count, batch_size, step_size, progress_bar)
    modelsList.append((models, hloss.__class__.__name__))
    p = predict(models, X_test)
    print(f"Hinge Loss Accuracy: {100 * (p == t_test).mean()}%")


    # Starts the Gui for interactive digit prediction
    root = tk.Tk()
    gui = DrawGUI(root)
    def on_digit_was_drawn(arr):
        x = arr.reshape(1, -1)         # shape (1, 784)
        x = np.hstack([x, np.ones((1, 1))])  # add bias term → shape (1, 785)
        predictList = []
        for models, name in modelsList:
            pred = predict(models, x)
            predictList.append(pred)
            print("Predicted digit for "+name+": ", pred[0])
            pred_text = "\n".join([f"{name} predicted {pred[0]}" for (pred, (models, name)) in zip(predictList, modelsList)])
        gui.pred_label.config(text=pred_text)

    gui.callback = on_digit_was_drawn 
    root.mainloop()
