#!/usr/bin/env python3

# If you are unfamiliar with PyTorch, we recommend you work through the 
# [PyTorch 60minutes Blitz](https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html) first.
# 
# For the exercises below, no prior knowledge of PyTorch is assumed.
# 
# Visit [this link](https://pytorch.org/tutorials/index.html) for some PyTorch tutorials.
# 
# All functions where you need to write code are indicated by `##### This is an exercise #####` in the doctsring.

import os
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from tqdm import trange
from typing import Tuple, List
from sklearn import datasets
from sklearn.model_selection import train_test_split

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchsummary import summary

def get_device() -> torch.device:
    """
    Set the torch device.
    This function is already fully implemented.
    """
    device = torch.device('cpu')  # We don't need the GPU for these assignments
    return device

def set_seed(random_seed:int=1000) -> None:
    """
    Set the seed.
    This function is already fully implemented.
    """
    random.seed(random_seed)
    os.environ['PYTHONHASHSEED'] = str(random_seed)
    np.random.seed(random_seed)
    torch.manual_seed(random_seed)

def get_dataset(random_seed:int, n_samples:int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Function to create a toy dataset for classification
    https://scikit-learn.org/stable/modules/generated/sklearn.datasets.make_moons.html

    This function is already fully implemented.
    """
    # Toy dataset
    moons = datasets.make_moons(
        n_samples=n_samples, 
        noise=.35, 
        random_state=random_seed
        )
    return moons

# Function for splitting into train and test sets
def split(dataset:Tuple[np.ndarray, np.ndarray], random_seed:int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Splits a dataset from sklearn into train and test sets.
    This function is already fully implemented.
    
    Args:
        dataset: sklearn dataset (data, labels) (2-tuple of numpy arrays)
    
    Returns: x_train, x_test, y_train, y_test (4-tuple of numpy arrays)
    """

    # Get data and labels
    X,Y = dataset

    # Reshape Y to [num_points, 1]
    Y = np.expand_dims(Y, axis=1)

    # Split the data into train and test sets
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=random_seed, train_size=0.75)
    
    print("Shape of data:")
    print(f"X_train: {X_train.shape}, X_test: {X_test.shape}, Y_train: {Y_train.shape}, Y_test: {Y_test.shape}")
    return X_train, X_test, Y_train, Y_test


def plot_decision_boundary(predict_fn, params, X_train, Y_train, X_test, Y_test, cmap='coolwarm'):
    """
    Plots the decision boundary predicted by the neural network.
    Don't worry about the details of this function.
    This function is already fully implemented.
    """

    fig, ax = plt.subplots(1,1)
    
    markers = ('s', '^', 'x', 'o', 'v')
    colors = ('red', 'blue', 'lightgreen', 'gray', 'cyan')
    cmap = ListedColormap(colors[:len(np.unique(Y_train))])

    # For constructing the grid limits
    h = 0.02
    x_min, x_max = X_train[:,0].min() - 10*h, X_train[:,0].max() + 10*h
    y_min, y_max = X_train[:,1].min() - 10*h, X_train[:,1].max() + 10*h
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    # Make predictions for each value inside the grid and reshape
    Z = predict_fn(params, np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    ax.contourf(xx, yy, Z, cmap=cmap, alpha=0.25)
    cs = ax.contour(xx, yy, Z, colors='k', alpha=1.0)
    
    for idx, yv in enumerate(np.unique(Y_train[:,0])): 
        ax.scatter(x=X_train[Y_train[:,0]==yv, 0], 
                    y=X_train[Y_train[:,0]==yv, 1], 
                    alpha=0.6, 
                    c=[cmap(idx)], 
                    marker=markers[0], 
                    s=20,
                    label=f"Train data class {yv}",
                    edgecolors='k')

    for idx, yv in enumerate(np.unique(Y_test[:,0])): 
        ax.scatter(x=X_test[Y_test[:,0]==yv, 0], 
                    y=X_test[Y_test[:,0]==yv, 1], 
                    alpha=0.6, 
                    c=[cmap(idx)], 
                    marker=markers[1], 
                    s=20,
                    label=f"Test data class {yv}",
                    edgecolors='k')
        
    ax.set_xlabel(r'$x_0$')
    ax.set_ylabel(r'$x_1$')
    ax.legend(ncol=2, fontsize=8)
    fig.savefig('decision_boundary.pdf', bbox_inches='tight')

def plot_loss(losses):
    """
    Plots the losses observed during training.
    This function is already fully implemented.
    """
    fig, ax = plt.subplots(1,1)
    ax.plot(losses)
    ax.set_xlabel('Iterations')
    ax.set_ylabel('Loss')
    fig.savefig('loss.pdf', bbox_inches='tight')

class Network(nn.Module):
    def __init__(
            self, 
            input_size: int, 
            hidden_size: int,
            hidden_num: int, 
            output_size: int=1
            ) -> None:
        """
        ##### This is an exercise #####

        Ex. 2.1: Fill in the missing pieces in the initialization function.

        This function initializes the Network class by creating the network layers.

        Args:
            input_size (int): The size of the input layer.
            hidden_size (int): The size of each hidden layer.
            hidden_num (int): The number of hidden layers.
            output_size (int): The size of the output layer.
        """

        super(Network, self).__init__()

        self.hidden_size = hidden_size
        self.input_size = input_size
        self.hidden_num = hidden_num
        self.output_size = output_size
        
        # This is like a list that will hold the layers
        self.layers = nn.ModuleList()
        
        # Fill `self.layers` with Linear layers
        # The first layer and the output layers are shown
        # Fill in the remaining hidden layers
        # NOTE: There should not be any ReLUs here
        
        # Here is an example to help you:
        # If input_size=2, hidden_size=3, hidden_num=2, output_size=1
        # then self.layers should contain the following:
        # Linear(2, 3), Linear(3, 3), Linear(3, 1)

        self.layers.append(nn.Linear(input_size, hidden_size))
        
        ### BEGIN SOLUTION
        raise NotImplementedError
        ### END SOLUTION
        
        # Output layer
        self.layers.append(nn.Linear(hidden_size, output_size))

    def forward(
            self, 
            x: torch.tensor) -> torch.tensor:
        """
        ##### This is an exercise #####

        Ex. 2.2: Fill in the missing pieces in the forward function.

        This function defines the forward pass of the neural network
        by passing the input x through all the layers and returns 
        the prediction made by the network.

        Args:
            x (torch.tensor): Input tensor with shape (batch_size, ...)
        Returns:
            torch.tensor: Output tensor (logits) after passing through the network.
        
        Steps:
            1. Flatten the input tensor `x` while keeping the batch dimension unchanged (done).
            2. Apply the ReLU activation function to the output of the first fully connected layer.
            3. Do this for each of the remaining hidden layers: apply the ReLU activation function to the output of the previous layer.
            4. Pass the output of the last hidden layer through the output layer without applying any activation function.
        Note:
            The final layer does not use an activation function because it typically outputs raw logits, 
            which are used for tasks like classification where a subsequent softmax or other activation is applied.
        """        

        # Flatten the non-batch dimensions
        x = x.view(-1, self.input_size)  

        ### BEGIN SOLUTION
        raise NotImplementedError  
        ### END SOLUTION
        
        # Return x (logits)
        return x 
    

def get_network(            
        input_size: int, 
        hidden_size: int,
        hidden_num: int, 
        output_size: int
    ) -> Network:
    """
    A wrapper to get a new network.
    This function is already fully implemented.
    """
    return Network(input_size, hidden_size, hidden_num, output_size)

def predict(
        net: Network, 
        x: np.ndarray) -> torch.tensor:
    """
    ##### This is an exercise #####

    Ex 2.3: Implement the prediction function.

    Function for producing network predictions. 
    This function takes the network (`net`) and the input data (`x`)
    and predicts the binary classification labels.
    To do so:
        1. First pass `x` through the network to get the logits
        2. Apply `torch.sigmoid(...)` to the logits
        3. Use a threshold of 0.5 on the sigmoid output to compute the final predicted class labels.
           (>0.5 means label should be 1, else 0)
    """
    
    # During evaluation we make sure that gradients are turned off
    net.eval()
    
    # Make predictions (class 0 or 1) using the learned parameters
    
    predictions = None
    # Computes probabilities using forward propagation, and classifies to 0/1 using 0.5 as the threshold.
    
    ### BEGIN SOLUTION
    raise NotImplementedError
    ### END SOLUTION

    return predictions

def calc_accuracy(Y_pred: np.ndarray, Y: np.ndarray) -> float:
    """
    ##### This is an exercise #####

    Ex. 2.4: Implement the accuracy function

    Calculates the accuracy of the predictions against the true labels
    (What percent of the predicted labels Y_pred matches the true labels in Y)
    
    Args:
        Y_pred: Predictions of our model (numpy array of shape [m,1] containing 0s and 1s)
        Y: (numpy array of shape [m,1])
        
    Returns: 
        accuracy (float between 0.0 and 1.0)
    
    """
    assert Y_pred.ndim == Y.ndim == 2
    assert Y_pred.shape == Y.shape
    assert Y_pred.shape[1] == 1
    
    ### BEGIN SOLUTION
    raise NotImplementedError
    ### END SOLUTION
    
    return accuracy

def train_network(
        net: Network, 
        inputs: np.ndarray, 
        labels: np.ndarray, 
        optimizer: torch.optim.SGD, 
        criterion: torch.nn.BCEWithLogitsLoss, 
        iterations:int=10000
        ) -> Tuple[Network,List[float]]:
    """
    ##### This is an exercise #####

    Ex. 2.5: Implement the training function that takes an untrained network,
    the training inputs and labels, the optimizer, the loss criterion and 
    trains the network for a given number of iterations. Comments are provided
    to guide your implementation.

    Function for training the PyTorch network.
    
    Args:
        net: the neural network object
        inputs: numpy array of training data values
        labels: numpy array of training data labels 
        optimizer: PyTorch optimizer instance
        criterion: Instance of a PyTorch loss criteria
        iterations: number of training steps
    """
    
    # Before training, set the network to training mode
    net.train()

    # It is a common practice to track the losses during training
    # Here we just use a list, but there are much better ways of logging this
    # e.g. wandb, tensorboard, etc.
    # In each iteration during training, the numerical value of the loss
    # should be appended to this list.
    losses = list()

    # Here we use a tiny dataset. So we can loop over the entire dataset multiple times
    for _ in trange(iterations):  

        # Get the inputs; data is a list of [inputs, labels]
        # Convert to tensors if data is in the form of numpy arrays
        if not torch.is_tensor(inputs):
            inputs = torch.from_numpy(inputs.astype(np.float32)) 
            
        if not torch.is_tensor(labels):
            labels = torch.from_numpy(labels.astype(np.float32))

        # Follow these steps:
        # 1. Reset gradients: Zero the parameter gradients
        # 2. Forward: Pass `inputs` through the network to produce `outputs` (logits)
        # 3. Compute the loss: Use `criterion(...)` and pass it the `outputs` and `labels`
        # 4. Backward: Call the `backward` function in `loss`
        # 5. Store the loss for returning later: `losses.append(loss.item())`
        # 6. Update parameters: This is done using the optimizer's `step` function. 
        
        ### BEGIN SOLUTION
        raise NotImplementedError
        ### END SOLUTION 
        
    # Return the trained network and list of training losses
    return net, losses


def train_evaluate(
        lr: float, 
        input_size: int,
        hidden_size: int,
        hidden_num: int,
        output_size: int,
        train_x: np.ndarray,
        train_y: np.ndarray,
        test_x: np.ndarray,
        test_y: np.ndarray,
        max_iters: int,
        do_plots:bool=True,
    ):
    """
    This is the full training pipeline, where you do the following:
        1. Initialize the network
        2. Set the loss criterion
        3. Initialize the optimizer 
        4. Train the network
        5. Compute the training and testing accuracy
        6. Plot the losses and the decision boundary
    
    This function is already fully implemented.
    """

    # Initialize the network using INPUT_SIZE, HIDDEN_SIZE, HIDDEN_NUM and OUTPUT_SIZE
    net = get_network(
        input_size=input_size,
        hidden_size=hidden_size,
        hidden_num=hidden_num,
        output_size=output_size
    ).float()

    # View the layers and number of trainable parameters
    summary(net, input_size=(2,))

    # Define the loss criterion 
    # Be careful, use binary cross entropy for binary, CrossEntropy for Multi-class
    criterion = nn.BCEWithLogitsLoss()  

    # Define the optimizer (use optim.SGD)
    optimizer = optim.SGD(
        net.parameters(), 
        lr=lr,
        momentum=0.9)

    # Train the network
    net, losses = train_network(
        net=net, 
        inputs=train_x, 
        labels=train_y, 
        optimizer=optimizer, 
        criterion=criterion, 
        iterations=max_iters
        )

    # Calculate the accuracies on the training and test data
    train_acc = calc_accuracy(
        predict(net, train_x).data.numpy(), 
        train_y
        )

    test_acc = calc_accuracy(
        predict(net, test_x).data.numpy(), 
        test_y
        )

    print(f"Train accuracy: {train_acc:.2f}, Test accuracy: {test_acc:.2f}")

    if do_plots:
        # Plot the loss function
        plot_loss(losses)

        # Plot the learned decision boundary
        plot_decision_boundary( 
            predict, 
            net, 
            train_x, 
            train_y, 
            test_x, 
            test_y)
    
    return train_acc, test_acc
    

if __name__ == '__main__':
    
    # DO NOT CHANGE!
    random_seed=42 
    set_seed(random_seed=random_seed)

    # Get the dataset
    moons = get_dataset(
        random_seed=random_seed, 
        n_samples=1000
        )

    # Split the dataset into train and test sets
    moons_x_train, moons_x_test, moons_y_train, moons_y_test = split(
        dataset=moons, 
        random_seed=random_seed
        )

    # Define hyperparameters
    LEARNING_RATE = 0.001
    MAX_ITERATIONS = 10000
    INPUT_SIZE = 2
    HIDDEN_SIZE = 10
    HIDDEN_NUM = 5
    OUTPUT_SIZE = 1

    # Train and evaluate
    train_acc, test_acc = train_evaluate(
        lr=LEARNING_RATE, 
        input_size=INPUT_SIZE,
        hidden_size=HIDDEN_SIZE,
        hidden_num=HIDDEN_NUM,
        output_size=OUTPUT_SIZE,
        train_x=moons_x_train,
        train_y=moons_y_train,
        test_x=moons_x_test,
        test_y=moons_y_test,
        max_iters=MAX_ITERATIONS,
    )