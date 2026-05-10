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

def get_true_y(x:np.ndarray):
    return 1.0 / (1.0 + np.exp(-((np.sin(2 * np.pi * x) * (1 + x)))))

def get_dataset(n_samples:int, sparsity=0.1, noise_scale=0.01) -> Tuple[np.ndarray, np.ndarray]:
    """
    Function to create a toy dataset for regression.
    This function is already fully implemented.
    """
    x_ = np.linspace(-1, 1, n_samples*2)

    n_neg = int(sparsity * n_samples)
    n_pos = n_samples - n_neg

    x = np.sort(
            np.concatenate(
                (
                    np.random.choice(x_[x_ < 0], n_neg, replace=False), 
                    np.random.choice(x_[x_ >= 0], n_pos, replace=False)
                )
            )
        )

    y = get_true_y(x) + np.random.normal(0, noise_scale, size=x.shape)

    x = x.reshape(-1, 1)
    y = y.reshape(-1, 1)

    return x, y

class Network(nn.Module):
    def __init__(
            self, 
            input_size: int, 
            hidden_size: int,
            hidden_num: int, 
            output_size: int=1
            ) -> None:
        """
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
        self.layers.append(nn.Linear(input_size, hidden_size))        
        for _ in range(hidden_num - 1):
            self.layers.append(nn.Linear(hidden_size, hidden_size))        
        self.layers.append(nn.Linear(hidden_size, output_size))

    def forward(
            self, 
            x: torch.tensor) -> torch.tensor:
        """
        This function defines the forward pass of the neural network
        by passing the input x through all the layers and returns 
        the prediction made by the network.

        Args:
            x (torch.tensor): Input tensor with shape (batch_size, ...)
        Returns:
            torch.tensor: Output tensor (logits) after passing through the network.
        
        Note:
            The final layer does not use an activation function because it typically outputs raw logits, 
            which are used for tasks like classification where a subsequent softmax or other activation is applied.
        """        

        # Flatten the non-batch dimensions
        x = x.view(-1, self.input_size)  

        for l in self.layers[:-1]:
            x = F.relu(l(x))            
        x = self.layers[-1](x)          
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
