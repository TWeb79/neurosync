"""
Test conftest and shared fixtures
Author: Inventions4All - github:TWeb79
"""

import pytest
import numpy as np


@pytest.fixture
def sample_rate():
    return 44100


@pytest.fixture
def sample_audio_data(sample_rate):
    duration = 0.1
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    left = np.sin(2 * np.pi * 220 * t)
    right = np.sin(2 * np.pi * 230 * t)
    return left, right