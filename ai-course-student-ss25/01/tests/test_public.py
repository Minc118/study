import numpy as np
import torch
from typing import Tuple, Union
import pytest

from solution_01 import set_seed, get_device, f1, f2, f3, opt_autograd, opt_finite_diff, solve_lineq_analytic, solve_lineq_sgd

# Test opt_autograd
@pytest.mark.parametrize(
    "loss_func, num_iters, best_theta",
    [
        (f1, 3000, np.array([0.0,0.0])),
        (f2, 3000, np.array([1.0, 3.0])),
    ]
)
def test_opt_autograd(
        loss_func:callable,
        num_iters:int,
        best_theta:np.array
    ):

    theta_dim = 2
    theta_min, theta_max = -2.0, 2.0
    lr = 0.05

    # Set the seed
    set_seed(42)  # DO NOT CHANGE

    # torch device is set to cpu
    torch.set_default_device(get_device())

    # torch optimization
    # Initialize theta - uniform random sampling
    theta = torch.rand(theta_dim) * (theta_max - theta_min) + theta_min
    
    theta.requires_grad = True  # Need to compute gradients for autograd

    theta_auto, _ = opt_autograd(
        theta=theta,
        loss_func=loss_func,
        num_iters=num_iters
    )

    np.testing.assert_allclose(
        theta_auto.detach().numpy(),
        best_theta,
        rtol=1e-3,
        atol=1e-5
    )


# Test opt_finite_diff
@pytest.mark.parametrize(
    "loss_func, num_iters, best_theta",
    [
        (f1, 3000, np.array([0.0,0.0])),
        (f2, 3000, np.array([1.0, 3.0])),
    ]
)
def test_opt_finite_diff(
        loss_func:callable,
        num_iters:int,
        best_theta:np.array,
    ):

    theta_dim = 2
    theta_min,  theta_max = -2.0, 2.0
    lr = 0.05

    # Set the seed
    set_seed(42)  # DO NOT CHANGE

    # torch device is set to cpu
    torch.set_default_device(get_device())

    # Finite differencing
    # Initialize theta - uniform random sampling
    theta = torch.rand(theta_dim) * (theta_max - theta_min) + theta_min

    theta.requires_grad = False  # FD does not need autograd

    theta_fd, _ = opt_finite_diff(
        theta=theta,
        loss_func=loss_func,
        num_iters=num_iters
    )

    np.testing.assert_allclose(
        theta_fd.detach().numpy(),
        best_theta,
        rtol=1e-3,
        atol=1e-5
    )

# Test solve_lineq_analytic
@pytest.mark.parametrize(
    "A, b, expected_x",
    [
        (
            torch.tensor([
                [2.0, -6.0, 6.0, -1.0],
                [-7.0, -7.0, -4.0, -3.0],
                [-2.0, 1.0, 6.0, 2.0],
                [8.0, -2.0, 6.0, 2.0]
            ]),
            torch.tensor([[92.0, -11.0, 9.0, 84.0]]).T,
            torch.tensor([[6.0, -5.0, 7.0, -8]]).T
        ),
        (
            torch.tensor([
                [2.0, -2.0, 1.0],
                [1.0, 3.0, -2.0],
                [3.0, -1.0, -1.0]
            ]),
            torch.tensor([[-3.0, 1.0, 2.0]]).T,
            torch.tensor([[-1.4, -2.0, -4.2]]).T
        ),
    ]
)
def test_solve_lineq_analytic(
        A: torch.Tensor, 
        b: torch.Tensor, 
        expected_x: torch.Tensor
    ):

    # Solve analytically
    x_analytic = solve_lineq_analytic(A, b)

    # Assert that the computed solution matches the expected solution
    torch.testing.assert_close(x_analytic, expected_x, rtol=1e-3, atol=1e-5)


# Test solve_lineq_analytic
@pytest.mark.parametrize(
    "A, b, expected_x",
    [
        (
            torch.tensor([
                [2.0, -6.0, 6.0, -1.0],
                [-7.0, -7.0, -4.0, -3.0],
                [-2.0, 1.0, 6.0, 2.0],
                [8.0, -2.0, 6.0, 2.0]
            ]),
            torch.tensor([[92.0, -11.0, 9.0, 84.0]]).T,
            torch.tensor([[6.0, -5.0, 7.0, -8]]).T
        ),
    ]
)
def test_solve_lineq_sgd(
        A: torch.Tensor, 
        b: torch.Tensor, 
        expected_x: torch.Tensor
    ):

    # Solve analytically
    x_sgd = solve_lineq_sgd(A, b)

    # Assert that the computed solution matches the expected solution
    torch.testing.assert_close(x_sgd, expected_x, rtol=1e-2, atol=1e-3)



