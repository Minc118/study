# Readme for Coding Assignment 03

## General Instructions

To obtain the code for this assignment, you will need to fetch and pull new commits from git@git.tu-berlin.de:lis-public/ai-course-student-ss25.git. Please refer to the instructions in [`00_README.md`](https://git.tu-berlin.de/lis-public/ai-course-student-ss25/-/blob/main/00/00_README.pdf?ref_type=heads).

As always, only modify the file `solution_??.py`. And even in `solution_??.py`, only modify what the functions do - don't change the function's names.

Run the following to install dependencies for this assignment. Remember to activate your virtual environment first.
```bash
# Activate virtual environment first
python3 -m pip install -r requirements_03.txt
```

Write your code only between `### BEGIN SOLUTION` and `### END SOLUTION` and remember to **replace** the line `raise NotImplementedError` with your code. Forgetting this may result in an exception and a grade of 0, even if your solution is correct:

```python
### BEGIN SOLUTION
#raise NotImplementedError << REMEMBER TO COMMENT OUT!

# Your code
a = b + c

### END SOLUTION
```

You can run tests by changing directory to the task folder `??`, and then simply typing `python3 -m pytest`. If you haven't yet, you will need to install pytest first. Please refer to the detailed setup-related instructions in [`00_README.md`](https://git.tu-berlin.de/lis-public/ai-course-student-ss25/-/blob/main/00/00_README.pdf?ref_type=heads).

## Bandits, with Discrete and Continuous Decision Space

### 1. UCB for standard Bandits

The objective of this exercise is to implement UCB1 for the standard bandit setting. The following information is available:
- There are $K$ possible choices for the action $a: \{0, \cdots ,K-1\}$ .
- Depending on your choice $a \in \{0,1,...,K-1\}$, we know that the outcome $r\sim P(r | a)$ will be strictly in the interval [0, 1] (i.e. $r \in [0,1]$). However, the true distribution $P(r|a)$ is not known.
- We have access to a stochastic environment that we can query $n$ times (using the function `env_step()`). Each time, the agent queries an action $a_i$, and the environment returns a reward $r_i$: `r = env_step(a)`, where, again, $r_i \in [0,1]$. Put differently, the agent makes $n$ data-collecting decisions to collect data $D=\{ (a_i, r_i)\}_{i=0}^{n-1}$.

##### (a) UCB for discrete actions [4 Pts]
For this exercise, you will need to modify the function `ucb_discrete(env_step, K, n)`. The inputs are:
- `env_step` is a function (Python `callable`) that simulates the outcome of the actions. It returns the outcome `r = env_step(a)` depending on the action $a \in \{0,1,...,K-1\}$.
- `K` is the number of actions that are possible. Your method must output an integer $a \in \{0,1,...,K-1\}$.
- `n` is the budget for querying the environment with `env_step`. If you query the environment more than $n$ times, an exception will be raised.

Complete the missing code in the function `ucb_discrete()` to return the best action according to the UCB1 algorithm. You can refer to slide numbers 5 and 11 in the [lecture slides](https://isis.tu-berlin.de/pluginfile.php/3559330/mod_resource/content/3/04-bandits.pdf).

### 2. UCB over Continuous Decisions using Bootstrapping

We consider the case where the decision variable $a\in[-1,1]$ is continuous in the interval $[-1,1]$. One could think of this as "infinite bandits". In this case, we cannot estimate a mean $\hat\mu_a$ *separately* for each $a$, but instead have to estimate a function $\hat\mu(a)$ over continuous $a$ using supervised machine learning. To also get a confidence interval you will implement bootstrapping. 

#### (a) Regression with a Neural Network [1+2 = 3 Pts]
You are given a data set $D=\{(a_i, r_i)_{i=0}^{n-1}\}$ of $n=50$ experiences that were already collected. You need to train a neural network to perform regression $\hat\mu(a)$ for this dataset. For this exercise, you need to complete the functions `predict()` and `regression()`. You will use the same neural network class `Network` that you used in exercise `02` (this is already provided to you). As previously, the `forward()` function of this class should not use an activation function for the output layer.
 
 - `predict()`: This function takes as input a neural network instance `net` and the inputs `a` and produces the regression outputs by first computing the `forward()` function of `net` and then applying the `sigmoid()` activation to ensure the predictions are in the range [0.0,1.0].
 - `regression()`: This function implements the training. You need to complete the main portion of this function. Your tasks include instantiating a suitable loss criteria for regression, initializing the `SGD` optimizer with the specified learning rate (also use `momentum=0.9`), and implementing the training loop similar to the classification example in exercise `02`. This function should return the trained `net` and a list of losses recorded during training. Comments have been provided in the code to guide you.

#### (b) Bootstrapping [1+2 = 3 Pts]
Generate $K$ bootstrapped resamples $\tilde D_k$ from the data $D$, as discussed on slide 04:19. For each $\tilde D_k$, train another neural network $\hat\mu_k(a)$. For this exercise, you need to complete the functions `resample_with_replacement()` and `bootstrap()`:

 - `resample_with_replacement()`: This function accepts a dataset $D=\{(a_i, r_i)_{i=0}^{n-1}\}$ and returns a resampled dataset $\tilde D$ of the same size by resampling from $D$ **with replacement**. Hint: Check the function `np.random.choice()`.
  - `bootstrap()`: This function implements the bootstrapping logic by creating $K$ bootstrapping resamples of the dataset $D$ (using `resample_with_replacement()`) and training a separate neural network on each of the $K$ data folds (using `regression()`). This function should return the list of $K$ trained networks.

#### (c) UCB action selection [2 Pts]
For a given list of real-valued actions $a$, (namely, $a=[-1, -0.5, 0.0, 0.5, 1]$), compute the mean $\hat\mu_a$ and standard deviation $\hat{\sigma}_a$ of the $K$ predictions $\mu_a \large|_{k=0,\cdots,K-1}$ for each action $a_i$. Which of the actions choices would UCB select?

For this exercise, modify the function `ucb_continuous()`. This function accepts a list of real-valued actions `a`, a list of networks `nets` (trained using `bootstrap()`) and first computes $\hat{\mu}_a$ and $\hat{\sigma}_a$ and then selects the best action $a^*$ using 
$$a^* = \arg\max\limits_a \hat{\mu}_a + \beta \hat{\sigma}_a$$

The function should return the best action $a^*$.

*Hint*: Make sure that $\hat{\mu}_a$ and $\hat{\sigma}_a$ have the same number of elements as $a$. However, note that $a$ will have the shape $(n,1)$ as this forms the input to the neural network. Since we know that each action is 1-dimensional, we can create $\hat{\mu}_a$ and $\hat{\sigma}_a$ as *flat* `np.ndarrays` with the shape $(n,)$ and the following assert (already provided) should pass:
```
assert r_hat_mean.shape == r_hat_std.shape == a.flatten().shape
```

*Note*: The value of $\beta$ is already provided in the code (do not change this).

#### (d) Plot [Optional, not graded]
Complete the function `create_plots` to plot $\hat\mu_a$ and $\hat\sigma_a$ over the interval $a \in [-1.0,1.0]$ and also plot the dataset $D$ with a `scatterplot`. You can execute this function by running the solution script after all the graded functions have been implemented: `python3 solution_03.py`. An example figure has been provided to show what this plot should look like (see the file `ucb_continuous.pdf`).

