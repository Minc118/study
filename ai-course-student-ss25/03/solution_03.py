import numpy as np
import matplotlib.pyplot as plt
from tqdm import trange
from typing import Tuple, List
import torch
import torch.nn as nn
import torch.optim as optim

from utils import set_seed, get_dataset, Network, get_network, get_true_y

def ucb_discrete(
        env_step: callable, 
        K: int, 
        n: int
    ) -> int:
    """
    UCB for standard Bandits (discrete actions). 
    See Q.1. in the readme for details about this task.
    """

    beta = 2.0  ## DO NOT CHANGE

    actions = np.arange(K)
    acc_returns = np.zeros(actions.shape)
    n_samples = np.zeros(actions.shape)

    best_action = None

    ### BEGIN SOLUTION
    raise NotImplementedError

    ### END SOLUTION
    best_action = np.argmax(acc_returns/n_samples)

    return best_action

def predict(
        net: Network, 
        a: np.ndarray,
        eval:bool=False) -> torch.tensor:
    """
    Prediction function for regression with a neural network.
    See Q.2(a) in the readme for details about this task.

    Function for producing network predictions. 
    This function takes the network (`net`) and the input data (`x`)
    and predicts the regression output. The output should be a real number between 0 and 1.
    """

    # Set to eval mode if not used during training
    if eval:
        net.eval()
        
    predictions = None
    
    if not torch.is_tensor(a):
        a = torch.from_numpy(a.astype(np.float32))

    ### BEGIN SOLUTION
    raise NotImplementedError

    ### END SOLUTION

    return predictions


def regression(
        dataset: Tuple[np.ndarray, np.ndarray],
        hidden_size:int, 
        hidden_num:int, 
        iterations:int,
        learning_rate:float,
    ) -> Tuple[Network, List[float]]:

    """
    Training logic for regression with a neural network.
    See Q.2(a) in the readme for details about this task.
    """

    # Get the inputs; data is a tuple of [x, y]
    a, r = dataset

    # Convert to tensors if data is in the form of numpy arrays
    if not torch.is_tensor(a):
        a_torch = torch.from_numpy(a.astype(np.float32)) 
        
    if not torch.is_tensor(r):
        r_torch = torch.from_numpy(r.astype(np.float32))

    # The input and output sizes are needed to create the network
    input_size = a.shape[1]
    output_size = r.shape[1]

    # Initialize the network
    net = get_network(
        input_size=input_size,
        hidden_size=hidden_size,
        hidden_num=hidden_num,
        output_size=output_size
    )

    # List to track losses
    losses = list()

    ### BEGIN SOLUTION
    raise NotImplementedError

    # Define the loss criterion 

    # Define the optimizer (use optim.SGD with momentum=0.9)

    # Training loop
        # Follow these steps:
        # 1. Reset gradients: Zero the parameter gradients
        # 2. Forward: Pass `inputs` through the network to produce `outputs`
        # 3. Compute the loss: Use `criterion(...)` and pass it the `outputs` and `labels`
        # 4. Backward: Call the `backward` function in `loss`
        # 5. Store the loss for returning later: `losses.append(loss.item())`
        # 6. Update parameters: This is done using the optimizer's `step` function. 
                    
    ### END SOLUTION
            
    return net, losses


def resample_with_replacement(
        dataset: Tuple[np.ndarray, np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Resampling with replacement for bootstrapping.
    See Q.2(b) in the readme for details about this task.
    """
    
    a, r = dataset
    assert a.shape[0] == r.shape[0]

    n_sample = a.shape[0]

    a_resampled, r_resampled = None, None
   
    ### BEGIN SOLUTION
    raise NotImplementedError

    ### END SOLUTION

    return a_resampled, r_resampled

def bootstrap(
        k:int,
        dataset: Tuple[np.ndarray, np.ndarray],
    ) -> List[Network]:
    """
    Logic for bootstrapping.
    See Q.2(b) in the readme for details about this task.
    """

    nets = list()

    ### BEGIN SOLUTION
    raise NotImplementedError

    ### END SOLUTION

    return nets

def ucb_continuous(a:np.ndarray, 
                   nets: List[Network],
                   beta:float=1.0
    ) -> float:
    """
    Logic for selecting continuous actions with UCB.
    See Q.2(c) in the readme for details about this task.
    """
    best_action = None

    k = len(nets)
    n = a.shape[0]

    # Used for storing the prediction for each action (in columns) and k (in rows)
    r_hats = np.zeros(shape=(k, n))

    # Mean and std (these need to be computed for selecting the best action)
    r_hat_mean = None
    r_hat_std = None

    ### BEGIN SOLUTION
    raise NotImplementedError

    ### END SOLUTION

    assert isinstance(best_action, float)
    assert r_hat_mean.shape == r_hat_std.shape == a.flatten().shape

    return best_action

def create_plots(n_samples=50, k=10, seed=100):
    """
    Plotting code (optional, not graded)
    """

    set_seed(seed)
    dataset = a,r = get_dataset(n_samples)
    nets = bootstrap(k=k, dataset=dataset) 

    ### BEGIN SOLUTION
    raise NotImplementedError

    ### END SOLUTION

if __name__ == "__main__":
    create_plots(n_samples=50, k=10, seed=100)