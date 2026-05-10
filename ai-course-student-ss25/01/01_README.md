# Readme for Coding Assignment 01

To obtain the code for this assignment, you will need to fetch and pull new commits from git@git.tu-berlin.de:lis-public/ai-course-student-ss25.git. Please refer to the instructions in [`00_README.md`](https://git.tu-berlin.de/lis-public/ai-course-student-ss25/-/blob/main/00/00_README.pdf?ref_type=heads).

As always, only modify the file `solution_??.py`. And even in `solution_??.py`, only modify what the functions do - don't change the function's names.

Remember to **replace** the line `raise NotImplementedError` with your code. Forgetting this may result in an exception and a grade of 0, even if your solution is correct.

You can run tests by changing directory to the task folder `??`, and then simply typing `python3 -m pytest`. If you haven't yet, you will need to install pytest first. Please refer to the detailed setup-related instructions in [`00_README.md`](https://git.tu-berlin.de/lis-public/ai-course-student-ss25/-/blob/main/00/00_README.pdf?ref_type=heads).


# Assignment 1: Optimization 
## 1.1: PyTorch SGD

You are provided with a vector $\theta \in \mathbb{R}^D$ (initialized to some value), and a callable function named `loss_func` that takes a single argument and returns a scalar loss. Your task is to find the value of $\theta$  that minimizes the `loss_func`. For this exercise, you will optimize $\theta$ to mimize `loss_func` using torch's SGD optimizer, by modifying the function `opt_autograd`. This function should return the optimized value of $\theta$ and loss value for the corresponding $\theta$.

You can find an example [here](https://pytorch.org/docs/stable/optim.html#taking-an-optimization-step).

This is the pseudocode:

    1. Define the optimizer # already implemented
    2. For i in range(num_iters):
        2.1. Reset the gradients
        2.2. Compute the loss value (output of loss_func for the current value of theta)
        2.3. Backpropagation step
        2.3. Update theta using the optimizer's step function
        2.5. If loss is NaN, stop optimization 
    3. Return theta and loss value

## 1.2: Finite Differencing

You are provided with a vector $\theta$ (initialized with some value),
and a callable function named `loss_func`. Your task is to find the 
value of `theta` that minimizes the `loss_func`. For this exercise, 
you will optimize `theta` to mimize `loss_func` using finite differencing, by modifying the function `opt_finite_diff`.
This function should return the optimized value of $\theta$ and loss value for the corresponding $\theta$.

Note that here `theta` will have `requires_grad = Fasle` and you are not allowed to use automatic differentiation.

This is the pseudocode:

    1. For i in range(num_iters):
        1.1. Compute the gradient of the loss function using finite differencing
        1.2. Update theta using the gradient
        1.3. If loss is NaN, stop optimization 
    2. Return theta and loss value

# Assignment 2: Solving a Linear Equation

## 2.1: Analytical Solution

Consider the equation $Ax = b$, where $A$ is a matrix, and
$b$ and $x$ are vectors. You are provided with $A$ and $b$, and
your task is to find the value of $x$ that solves the given 
equation. You can assume that there is a unique solution. Plese modify the
function `solve_lineq_analytic`.

For this exercise, find $x$ in a single step using the 
closed-form analytical solution. 

This function should return the solved value of $x$.

## 2.2: Solution via SGD

Consider the equation $Ax = b$, where $A$ is a matrix, and
$b$ and $x$ are vectors. You are provided with $A$ and $b$, and
your task is to find the value of $x$ that solves the given 
equation. You can assume that there is a unique solution.

For this exercise, you will use the SGD optimizer from torch
to find $x$ in an iterative way. The code for setting up the 
optimizer and the loss function is already provided. You need 
to write the optimization loop similar to the pseudocode 
in exercise 1.1, but note that here the function `loss_func` 
takes 2 arguments.  Plese modify the
function `solve_lineq_sgd`.

This function should return the solved value of $x$.
