"""
"""

import numpy as np


def gini_index(x):
    
    x = np.sort(x)
    total = np.sum(x)
    N = len(x)
    
    # if the input is empty or the total is 0, then the distribution is uniform
    if N == 0 or total < 1e-9:
        return 0 # G_min
    else:
        G_max = 1 - 1 / N
        G_bar = np.dot(np.arange(1, N + 1), x) / (N * total)
        return round(G_max - 2 * (1 - G_bar), 2)


def lorenz_curve(x):
    
    x = np.sort(x)
    N = len(x)
    
    if N == 0:
        raise ValueError("Lorenz curve computation requires at least one individual.")
    
    total = np.sum(x)
    if total < 1e-9:
        return np.zeros_like(x), np.zeros_like(x)
    
    cumulative_share = np.cumsum(x) / total
    population_share = np.linspace(0, 1, N)
    
    return cumulative_share, population_share
