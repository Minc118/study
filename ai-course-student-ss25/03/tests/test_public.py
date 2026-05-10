"""
Test cases for you to check your solutions.
run by typing `pytest` in the task folder.
Do not change the content of this file!
"""
import numpy as np
import pytest
import torch

from utils import get_device, set_seed, get_true_y, get_dataset, Network, get_network
from solution_03 import predict, regression, resample_with_replacement, bootstrap, ucb_continuous, ucb_discrete

# Set the seed ## DO NOT CHANGE
SEED = 100

### Test ucb_discrete ###

class SimulatorBase():
    """
    Simulator: Base class
    """
    def __init__(self, n):
        self.counter = 0
        self.n = n
    
    def increment_counter(self):
        """
        Helper method
        """
        self.counter += 1

        if self.counter > self.n:
            raise Exception("You exceeded the maximum allowed number of queries")

    def simulate_outcome(self, a):
        """
        Simulate the outcome of action a
        """
        raise NotImplementedError

class DeterministicSimulator(SimulatorBase):
    """
    Deterministic return
    """
    def __init__(self, n):
        super().__init__(n)
        self.deterministic_returns = np.array([
            0.2, 0.4, 0.6, 0.1, 0.0, 0.3
        ])

    def simulate_outcome(self, a):
        if hasattr(a, "__len__"):
            raise Exception("Action a is non-scalar")
        self.increment_counter()
        return self.deterministic_returns[a]

class BinarySimulator(SimulatorBase):
    """
    Return 0 with probability p_a
    Return 1 with probability 1 - p_a
    p_a depends on action a
    """
    def __init__(self, n):
        super().__init__(n)
        self.A = 6

    def simulate_outcome(self, a):
        self.increment_counter()
        if a==0:
            return float(
                np.random.rand() > 0.7
            )
        elif a==1:
            return float(
                np.random.rand() > 0.1
            )
        elif a==2:
            return float(
                np.random.rand() > 0.5
            )
        elif a==3:
            return float(
                np.random.rand() > 0.9
            )
        elif a==4:
            return float(
                np.random.rand() > 0.3
            )
        elif a==5:
            return float(
                np.random.rand() > 0.99
            )
        else:
            raise Exception("Invalid action a")

class PiecewiseUniformSimulator(SimulatorBase):
    """
    Piecewise uniform distribution
    """
    def __init__(self, n):
        super().__init__(n)
        self.A = 7

    def simulate_outcome(self, a):
        self.increment_counter()
        if a==0:
            border = 0.9
            p_left = 0.5
        elif a==1:
            border = 0.1
            p_left = 0.5
        elif a==2:
            border = 0.9
            p_left = 0.05
        elif a==3:
            border = 0.5
            p_left = 0.05
        elif a==4:
            border = 0.96
            p_left = 0.99
        elif a==5:
            border = 0.3
            p_left = 0.5
        elif a==6:
            border = 0.3
            p_left = 0.9
        else:
            raise Exception("Invalid action a")

        if np.random.rand() < p_left:
            return border * np.random.rand()
        return border + (1-border) * np.random.rand()

test_cases = []

# 2 test cases for DeterministicSimulator
for n in [100, 10]:
    # instantiate simulator
    simulator_object = DeterministicSimulator(n)
    A = len(simulator_object.deterministic_returns)
    env_step = simulator_object.simulate_outcome

    # create input
    test_cases.append((
        env_step,
        A,
        n,
        2
    ))

@pytest.mark.parametrize(
    "env_step,A,n,best_action",
    test_cases
)
def test_ucb_discrete(env_step, A, n, best_action):
    set_seed(random_seed=SEED)
    assert best_action == ucb_discrete(env_step, A, n)


### Tests for predict and regression  ###

@pytest.mark.parametrize(
    "hidden_size, hidden_num, n_samples, all_tests_pass",
    [
        [50, 2, 50, True],
    ]
)
def test_predict(hidden_size, hidden_num, n_samples, all_tests_pass):
    set_seed(random_seed=SEED)

    input_size = output_size = 1

    # Random input
    x = torch.rand(n_samples, input_size) * 2 - 1 
    
    # Initialize the network
    net = get_network(
        input_size=input_size,
        hidden_size=hidden_size,
        hidden_num=hidden_num,
        output_size=output_size
    )

    y_hat = predict(net, x, eval=True)

    test_a = isinstance(y_hat, torch.Tensor)
    test_b = np.all((0.0 <= y_hat.detach().numpy()) & (y_hat.detach().numpy() <= 1.0))
    test_c = y_hat.shape == (n_samples, output_size)
    
    assert test_a, "predict should return a torch tensor"
    assert test_b, "outputs should be between 0.0 and 1.0"
    assert test_c, "output shape is incorrect"

    assert all_tests_pass == test_a and test_b and test_c

@pytest.mark.parametrize(
    "n_samples, all_tests_pass",
    [
        [50, True],
    ]
)
def test_regression(n_samples, all_tests_pass):
    set_seed(random_seed=SEED)

    dataset = x, y = get_dataset(n_samples)

    net, losses = regression(
        dataset=dataset,
        hidden_num=2,
        hidden_size=30,
        iterations=2_000,
        learning_rate=1e-1
    )

    y_hat = predict(net, x, eval=True)

    test_a = np.all((0.0 <= y_hat.detach().numpy()) & (y_hat.detach().numpy() <= 1.0))
    test_b = losses[0] > losses[-1]
    test_c = np.linalg.norm(y_hat.detach().numpy() - y)/n_samples < 0.01

    assert test_a, "outputs should be between 0.0 and 1.0"
    assert test_b, "loss should decrease during training"
    assert test_c, "predictions are not accurate"

    assert all_tests_pass == test_a and test_b and test_c


### Tests for Bootstrapping  ###
@pytest.mark.parametrize(
    "n_samples, all_tests_pass",
    [
        [50, True],
    ]
)
def test_resample(n_samples, all_tests_pass):
    set_seed(random_seed=SEED)

    dataset = x, y = get_dataset(n_samples)
    x_resampled, y_resampled = resample_with_replacement(dataset)

    test_a = x.shape == x_resampled.shape
    test_b = y.shape == y_resampled.shape
    assert test_a and test_b, "Dataset shapes should not change"

    test_c = not np.array_equal(x, x_resampled)
    test_d = not np.array_equal(y, y_resampled)
    assert test_c and test_d, "Resampled dataset should not be the same as the original"

    test_e = np.unique(x.flatten()).shape[0] > np.unique(x_resampled.flatten()).shape[0]
    test_f = np.unique(y.flatten()).shape[0] > np.unique(y_resampled.flatten()).shape[0]
    assert test_e and test_f, "The original dataset should have more unique data points"

    assert all_tests_pass == test_a and test_b and test_c and test_d and test_e and test_f

@pytest.mark.parametrize(
    "n_samples, k, all_tests_pass",
    [
        [50, 10, True],
    ]
)
def test_bootstrap(n_samples, k, all_tests_pass):
    set_seed(random_seed=SEED)

    dataset = get_dataset(n_samples)
    nets = bootstrap(k=k, dataset=dataset)

    a_eval = np.linspace(-1, 1, 100)
    r_hats = np.zeros(shape=(k, a_eval.shape[0]))
    r_eval = get_true_y(a_eval)
    for j in range(k):
        r_hats[j] = predict(nets[j], a_eval).detach().numpy().flatten()

    r_hat_mean = np.mean(r_hats, axis=0)
    r_hat_std = np.std(r_hats, axis=0)

    r_hat_std = r_hat_std.flatten()
    uncertainty_first = np.mean(r_hat_std[0:r_hat_std.shape[0]//2])
    uncertainty_second = np.mean(r_hat_std[r_hat_std.shape[0]//2:]) 
    test_a = uncertainty_first >= uncertainty_second

    assert test_a, "Uncertainty should be higher for -1.0<a_i<0.0 than for 0.0<a_i<1.0"

    if k==1:
        assert uncertainty_first == 0.0 and uncertainty_second == 0.0, "STD should be 0.0 for a single fold"

    assert all_tests_pass == test_a

### Tests for continuous action selection ###
@pytest.mark.parametrize(
    "a, k, n_samples, best_action",
    [
        [np.array([[-1.0, -0.5, 0.0, 0.5, 1.0]]).T, 10, 50, -1.0],
    ]
)
def test_ucb_continuous(a, k, n_samples, best_action):
    set_seed(random_seed=SEED)

    dataset = get_dataset(n_samples)
    nets = bootstrap(k=k, dataset=dataset)        
    best_action_ = ucb_continuous(nets=nets, a=a)

    assert isinstance(best_action_, float)
    assert best_action == best_action_


