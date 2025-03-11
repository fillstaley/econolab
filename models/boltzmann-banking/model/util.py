"""
"""


def gini_index(x):
    x = sorted(x)
    N = len(x)
    X = sum(x)
    
    G_max = 1 - 1 / N
    G_bar = sum(i * x_i for i, x_i in enumerate(x, start=1)) / (N * X) if X else (N + 1) / (2 * N)
    
    return round(G_max - 2 * (1 - G_bar), 2) if X else 0
