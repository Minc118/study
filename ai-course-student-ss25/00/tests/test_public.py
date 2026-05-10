"""
Test cases for you to check your solutions.
run by typing `pytest` in the task folder.
Do not change the content of this file!
"""
import numpy as np
import pytest

from solution_00 import is_even_and_positive

@pytest.mark.parametrize(
    "input,output",
    [
        (0.0, False),
        (200, True),
        (-11, False),
        (-34, False),
        (-2.9, False),
        (30, True)
    ]
)
def test_is_even_and_positive(input, output):
    assert output == is_even_and_positive(input)
