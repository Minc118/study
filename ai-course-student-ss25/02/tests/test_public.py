import numpy as np
import torch
from typing import Tuple
import pytest
from sklearn import datasets

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from solution_02 import get_device, set_seed, get_network, split
from solution_02 import predict, calc_accuracy, train_network

def get_dataset_multi(
        random_seed:int, 
        n_samples:int,
        name:str='moons',
    ) -> Tuple[np.ndarray, np.ndarray]:

    if name == 'moons':
        return datasets.make_moons(
                n_samples=n_samples, 
                noise=.35, 
                random_state=random_seed
            )
    elif name=='blobs':
        return datasets.make_blobs(
            n_samples=n_samples,
            centers=2, 
            cluster_std=0.5, 
            random_state=random_seed
        )
    elif name=='circles':
        return datasets.make_circles(
            n_samples=n_samples,
            noise=0.1, 
            factor=0.3, 
            random_state=0
        )
    else:
        raise NotImplementedError(f"Unknown dataset {name}")


@pytest.mark.parametrize(
    "input_size, hidden_size, hidden_num, output_size, layer_shapes",
    [
        (1, 100, 2, 1, [(1, 100), (100, 100), (100, 1)]),
    ]
)
def test_init(
        input_size,
        hidden_size,
        hidden_num,
        output_size,
        layer_shapes
    ):

    # DO NOT CHANGE!
    random_seed=42 
    set_seed(random_seed=random_seed)
    torch.set_default_device(get_device())

    net = get_network(
        input_size=input_size,
        hidden_size=hidden_size,
        hidden_num=hidden_num,
        output_size=output_size
    ).float()

    for l, shape in zip(net.layers, layer_shapes):
        assert isinstance(l, nn.Linear)
        assert l.in_features == shape[0]
        assert l.out_features == shape[1]


@pytest.mark.parametrize(
    "input_size, hidden_size, hidden_num, output_size, batch_size",
    [
        (1, 100, 2, 1, 750),
        (5, 10, 7, 10, 50),
    ]
)
def test_forward(
        input_size,
        hidden_size,
        hidden_num,
        output_size,
        batch_size,
    ):

    # DO NOT CHANGE!
    random_seed=42 
    set_seed(random_seed=random_seed)
    torch.set_default_device(get_device())

    net = get_network(
        input_size=input_size,
        hidden_size=hidden_size,
        hidden_num=hidden_num,
        output_size=output_size
    ).float()

    dummy_x = torch.rand(batch_size, input_size).float()
    dummy_x = dummy_x.view(-1, input_size) 

    dummy_out = net(dummy_x).detach()

    assert dummy_out.shape == (batch_size, output_size)

    dummy_hidden_f = F.relu(torch.rand(batch_size, hidden_size)).float()

    out_layer = net.layers[-1]
    out_w = out_layer.weight.detach()
    out_b = out_layer.bias.detach()

    expected_out = F.linear(dummy_hidden_f, out_w, out_b).detach()
    dummy_last_out = out_layer(dummy_hidden_f).detach()

    assert torch.equal(expected_out, dummy_last_out)


@pytest.mark.parametrize(
    "input_size, hidden_size, hidden_num, output_size, batch_size",
    [
        (2, 20, 3, 4, 20),
        (5, 10, 5, 20, 150),
    ])
def test_predict(        
        input_size,
        hidden_size,
        hidden_num,
        output_size,
        batch_size,
    ):

    # DO NOT CHANGE!
    random_seed=42 
    set_seed(random_seed=random_seed)
    torch.set_default_device(get_device())

    net = get_network(
        input_size=input_size,
        hidden_size=hidden_size,
        hidden_num=hidden_num,
        output_size=output_size
    ).float()

    dummy_x_np = np.random.rand(batch_size, input_size)
    dummy_out = predict(net=net, x=dummy_x_np)

    assert isinstance(dummy_out, torch.Tensor), "Prediction must be of type torch.Tensor"
    assert dummy_out.shape == (batch_size, output_size), "Predicted output has wrong shape"
    
    dummy_out_flat = dummy_out.view(-1)
    assert torch.all((dummy_out_flat == 0) | (dummy_out_flat == 1)), "Prediction contains values other than 0 and 1"

@pytest.mark.parametrize(
    "y_pred, y, req_accuracy",
    [
        (np.array([[1,1,1,1,1]]).T, np.array([[1,1,1,1,1]]).T, 1.0),
        (np.array([[0,0,0,0,0]]).T, np.array([[1,1,1,1,1]]).T, 0.0),
    ])
def test_calc_accuracy(y_pred, y, req_accuracy):
    accuracy = calc_accuracy(y_pred, y)
    assert 0.0 <= accuracy <= 1.0, "Accuracy should be between 0.0 and 1.0"
    assert accuracy == req_accuracy, f"Accuracy should be {req_accuracy} instead of {accuracy}"

@pytest.mark.parametrize(
    "input_size, hidden_size, hidden_num, output_size, dataset_name",
    [
        (2, 20, 3, 1, "moons"),
    ])
def test_train_network(
        input_size,
        hidden_size,
        hidden_num,
        output_size,
        dataset_name,
    ):

    # DO NOT CHANGE!
    random_seed=42 
    set_seed(random_seed=random_seed)
    torch.set_default_device(get_device())

    # Get the dataset
    dataset = get_dataset_multi(
        random_seed=random_seed, 
        n_samples=200,
        name=dataset_name,
        )

    # Split the dataset into train and test sets
    x_train, x_test, y_train, y_test = split(
        dataset=dataset, 
        random_seed=random_seed
        )

    # Define hyperparameters
    LEARNING_RATE = 0.001
    MAX_ITERATIONS = 10000

    net = get_network(
        input_size=input_size,
        hidden_size=hidden_size,
        hidden_num=hidden_num,
        output_size=output_size
    ).float()

    criterion = nn.BCEWithLogitsLoss()  
    optimizer = optim.SGD(net.parameters(), lr=LEARNING_RATE, momentum=0.9)

    # Evaluate training function
    net, losses = train_network(
        net=net, 
        inputs=x_train, 
        labels=y_train, 
        optimizer=optimizer, 
        criterion=criterion, 
        iterations=MAX_ITERATIONS
        )
    
    assert losses[0] > losses[-1], f"The final loss should be smaller than the initial loss"

    train_acc = calc_accuracy(
        predict(net, x_train).data.numpy(), 
        y_train
        )

    test_acc = calc_accuracy(
        predict(net, x_test).data.numpy(), 
        y_test
        )
    
    # Here we use a threshold - the test passes only if the accuracy is above 60%
    assert 0.6 < train_acc <= 1.0, f"Train accuracy is {train_acc:.2f} but it should be above 0.6"
    assert 0.6 < test_acc <= 1.0, f"Test accuracy is {test_acc:.2f} but it should be above 0.6"


