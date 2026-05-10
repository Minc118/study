import os
import random
import numpy as np
import torch
from typing import Tuple, Union


def get_device() -> torch.device:
    device = torch.device('cpu')  # We don't need the GPU for these assignments
    return device


def set_seed(seed:int=1000) -> None:
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    

def f1(x: Union[torch.Tensor, np.ndarray]) -> Union[torch.Tensor, np.ndarray]:
    if isinstance(x, np.ndarray):
        return np.sum(x ** 2)
    elif isinstance(x, torch.Tensor):
        return torch.sum(x ** 2)


def f2(x: Union[torch.Tensor, np.ndarray]) -> Union[torch.Tensor, np.ndarray]:
    x1 = x[0]
    x2 = x[1]
    return (x1 + 2 * x2 - 7) ** 2 + (2 * x1 + x2 - 5) ** 2


def f3(x: torch.Tensor) -> torch.Tensor:
    x1 = x[0]
    x2 = x[1]
    return 0.26 * (x1 ** 2 + x2 ** 2) - 0.48 * x1 * x2


# Set the seed
set_seed(42)  # DO NOT CHANGE


### Exercise 1.1
def opt_autograd(
      theta:torch.Tensor,  
      loss_func:callable,
      num_iters:int=1000,   # DO NOT CHANGE
      lr:float=0.05         # DO NOT CHANGE
    ) -> Tuple[torch.Tensor, float]:

    """
    You are provided with a vector `theta` (initialized with some value),
    and a callable function named `loss_func` that takes a single argument and
    returns a scalar loss. Your task is to find the value of `theta` that 
    minimizes the `loss_func`. For this exercise, you will optimize `theta` 
    to mimize `loss_func` using torch's SGD optimizer.

    You can find an example here: https://pytorch.org/docs/stable/optim.html#taking-an-optimization-step

    This is the pseudocode:

    1. Define the optimizer # already implemented
    2. For i in range(num_iters):
        2.1. Reset the gradients
        2.2. Compute the loss value (output of loss_func for the current value of theta)
        2.3. Backpropagation step
        2.3. Update theta using the optimizer's step function
        2.5. If loss is NaN, stop optimization 
    3. Return theta and loss value

    """
    # Define the optimizer
    optimizer = torch.optim.SGD([theta], lr=lr)

    # Replace `raise NotImplementedError` with your code
    raise NotImplementedError
    

### Exercise 1.2
def opt_finite_diff(
      theta: torch.Tensor,
      loss_func: callable,
      num_iters:int=1000,   # DO NOT CHANGE
      lr:float=0.05         # DO NOT CHANGE
    ) -> Tuple[torch.Tensor, float]:

    """
    You are provided with a vector `theta` (initialized with some value),
    and a callable function named `loss_func`. Your task is to find the 
    value of `theta` that minimizes the `loss_func`. For this exercise, 
    you will optimize `theta` to mimize `loss_func` using finite differencing.

    Note that here `theta` will have `requires_grad = Fasle`
    This is the pseudocode:

    1. For i in range(num_iters):
        1.1. Compute the gradient of the loss function using finite differencing
        1.2. Update theta using the gradient
        1.3. If loss is NaN, stop optimization 
    2. Return theta and loss value

    """
    # Replace `raise NotImplementedError` with your code
    raise NotImplementedError


### Exercise 2.1
def solve_lineq_analytic(
        A: torch.tensor,
        b: torch.tensor
    ) -> torch.tensor:
    """
    Consider the equation Ax = b, where A is a matrix, and
    b and x are vectors. You are provided with A and b, and
    your task is to find the value of x that solves the given 
    equation. You can assume that there is a unique solution.

    For this exercise, find x in a single step using the 
    closed-form analytical solution. 

    This function should return the solved value of x.
    """

    # Replace `raise NotImplementedError` with your code
    raise NotImplementedError
    
    # Return solution for x
    return x


### Exercise 2.2
def solve_lineq_sgd(
        A: torch.tensor,
        b: torch.tensor,
        lr:float=0.005,  # DO NOT CHANGE
        num_iters:int=20_000,  # DO NOT CHANGE
    ) -> torch.tensor:
    """
    Consider the equation Ax = b, where A is a matrix, and
    b and x are vectors. You are provided with A and b, and
    your task is to find the value of x that solves the given 
    equation. You can assume that there is a unique solution.

    For this exercise, you will use the SGD optimizer from torch
    to find x in an iterative way. The code for setting up the 
    optimizer and the loss function is already provided. You need 
    to write the optimization loop similar to the pseudocode 
    in exercise 1.1, but note that here the function `loss_func` 
    takes 2 arguments.

    This function should return the solved value of x.
    """

    # Initialize x and turn on gradient computations
    x = torch.normal(0.0, 1.0, size=b.size(), requires_grad=True)  # DO NOT CHANGE

    # Define the optimizer
    optimizer = torch.optim.SGD([x], lr=lr)  # DO NOT CHANGE
    
    # Define the loss function
    # This function should give the difference between Ax and b
    # When x is optimized (i.e. when the equation is solved),
    # the loss function will have a value of 0 (or close to 0 since SGD is used here).
    loss_func = torch.nn.MSELoss()  # DO NOT CHANGE

    # Replace `raise NotImplementedError` with your code
    raise NotImplementedError
    
    # Return solution for x
    return x