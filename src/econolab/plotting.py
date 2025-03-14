"""A collection of visualization functions.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def money_supply(model, period: int = 1):
    """Plot the money supply and its change over time, with separate visualization for issued and repaid debt.

    Parameters:
    -----------
    model : Mesa model
        The simulation model containing the collected data.
    period : int, optional (default=1)
        The number of steps to aggregate over. Used for rolling sums and downsampling.

    """
    # Extract model-level data
    model_df = model.datacollector.get_model_vars_dataframe()

    # Ensure necessary columns exist
    required_columns = {"Money Supply", "Issued Debt", "Repaid Debt"}
    missing = required_columns - set(model_df.columns)
    if missing:
        raise ValueError(f"Missing expected columns in model dataframe: {missing}")

    # Compute money supply change (Net Debt Issuance) as a rolling sum over the specified period
    model_df["Issued Debt"] = model_df["Issued Debt"].rolling(period).sum()
    model_df["Repaid Debt"] = model_df["Repaid Debt"].rolling(period).sum()
    model_df["Money Supply Change"] = model_df["Issued Debt"] - model_df["Repaid Debt"]

    # Downsample the data by selecting every 'period' step
    sampled_df = model_df.iloc[::period]

    # Create figure with two vertically stacked axes
    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

    ## **First Plot: Total Money Supply**
    axes[0].plot(sampled_df.index, sampled_df["Money Supply"], label="Money Supply", color="blue")
    axes[0].set_ylabel("Money Supply")
    axes[0].set_title(f"Money Supply Over Time (Downsampled every {period} steps)")
    axes[0].legend()
    axes[0].grid(True)

    ## **Second Plot: Issued Debt & Net Issuance**
    axes[1].plot(sampled_df.index, sampled_df["Money Supply Change"], label="Net Issuance", color="black")
    axes[1].plot(sampled_df.index, sampled_df["Issued Debt"], label="Issued Debt", color="black", linestyle="dashed")

    # **Shading between Issued Debt and Net Issuance ("Less Debt Repaid")**
    axes[1].fill_between(
        sampled_df.index,
        sampled_df["Issued Debt"],
        sampled_df["Money Supply Change"],
        interpolate=True,
        color="gray",
        alpha=0.3,
        label="Less Debt Repaid"
    )

    # **Shading for positive/negative net issuance**
    axes[1].fill_between(
        sampled_df.index,
        sampled_df["Money Supply Change"], 
        0,
        where=(sampled_df["Money Supply Change"] > 0),
        interpolate=True,
        color="green",
        alpha=0.3,
        label="Money Supply Growing"
    )

    axes[1].fill_between(
        sampled_df.index,
        sampled_df["Money Supply Change"], 
        0,
        where=(sampled_df["Money Supply Change"] < 0),
        interpolate=True,
        color="red",
        alpha=0.3,
        label="Money Supply Shrinking"
    )

    axes[1].set_ylabel(f"Change in Money Supply (Rolling {period}-Step Sum)")
    axes[1].set_xlabel("Steps")
    axes[1].set_title(f"Change in Money Supply Over Time (Rolling {period}-Step Sum)")
    axes[1].legend()

    # Improve layout and show plot
    plt.tight_layout()
    plt.show()


def individual_wealth_inequality(model, p_values = [0.25, 0.5, 0.75]):
    
    # Extract model-level data
    model_df = model.datacollector.get_model_vars_dataframe()

    individual_wealth_gini = model_df["Individual Wealth Gini"]
    
    steps = individual_wealth_gini.index.get_level_values(0).unique()
    wealth_share_over_time = {p: [] for p in p_values}

    for step in steps:
        for p in p_values:
            wealth_share_over_time[p].append(model.lorenz_wealth_value(step, p))

    # Create a stacked figure
    fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    
    # Plot Gini coefficient
    ax[0].plot(steps, individual_wealth_gini, marker="o", linestyle="-", color="red")
    ax[0].set_ylabel("Gini Coefficient")
    ax[0].set_title("Gini Coefficient and Wealth Share Over Time")
    ax[0].grid(True)
    ax[0].set_ylim(0, 1)
    
    # Plot wealth share of bottom p%
    for p in p_values:
        ax[1].plot(steps, wealth_share_over_time[p], marker="o", linestyle="-", label=f"Bottom {p}%")
    ax[1].set_xlabel("Time Step")
    ax[1].set_ylabel("Wealth Share (%)")
    ax[1].legend()
    ax[1].grid(True)
    ax[1].set_ylim(0, 1)
    
    plt.tight_layout()
    plt.show()


def individual_wealth_distribution(model, step: int | None = None):
    
    if step is None:
        step = model.steps
    
    wealth_data = model.individual_data["Wealth"].xs(step, level=0)
    
    total_wealth = np.sum(wealth_data)
    sorted_wealth = np.sort(wealth_data)
    cumulative_wealth = np.cumsum(sorted_wealth) / total_wealth if total_wealth else 0
    population_share = np.linspace(0, 1, len(sorted_wealth))
    
    # Create figure with two subplots
    fig, ax = plt.subplots(1, 2, figsize=(8, 3))

    # Histogram of wealth distribution
    sns.histplot(wealth_data, bins=20, kde=True, ax=ax[0], color="blue")
    ax[0].set_title(f"Wealth Distribution (Step {step})")
    ax[0].set_xlabel("Wealth")
    ax[0].set_ylabel("Number of Agents")

    # Lorenz Curve
    ax[1].plot(population_share, cumulative_wealth, label="Lorenz Curve", color="red")
    ax[1].plot([0, 1], [0, 1], linestyle="--", color="black", label="Perfect Equality")
    ax[1].set_title(f"Lorenz Curve of Wealth (Step {step})")
    ax[1].set_xlabel("Cumulative Population Share")
    ax[1].set_ylabel("Cumulative Wealth Share")
    ax[1].legend()

    plt.tight_layout()
    plt.show()


def individual_income_inequality(model, p_values: list[float] = [0.25, 0.5, 0.9]):
    """
    Plots the Gini coefficient of individual income over time and the wealth share of the bottom p%.
    """
    model_df = model.datacollector.get_model_vars_dataframe()
    individual_income_gini = model_df["Individual Income Gini"]
    
    steps = individual_income_gini.index.get_level_values(0).unique()
    income_share_over_time = {p: [] for p in p_values}

    for step in steps:
        for p in p_values:
            income_share_over_time[p].append(model.lorenz_income_value(step, p))
    
    fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    
    # Plot Gini coefficient
    ax[0].plot(steps, individual_income_gini, marker="o", linestyle="-", color="blue")
    ax[0].set_ylabel("Gini Coefficient")
    ax[0].set_title("Gini Coefficient and Income Share Over Time")
    ax[0].grid(True)
    ax[0].set_ylim(0, 1)
    
    # Plot income share of bottom p%
    for p in p_values:
        ax[1].plot(steps, income_share_over_time[p], marker="o", linestyle="-", label=f"Bottom {p}%")
    ax[1].set_xlabel("Time Step")
    ax[1].set_ylabel("Income Share (%)")
    ax[1].legend()
    ax[1].grid(True)
    ax[1].set_ylim(0, 1)
    
    plt.tight_layout()
    plt.show()


def individual_income_distribution(model, step: int | None = None):
    """
    Plots the income distribution histogram and Lorenz curve for a given step.
    """
    if step is None:
        step = model.steps
    
    # extract the data to be plotted
    income_data = model.individual_data["Income"].xs(step, level=0)
    pop_share, cum_income = model.lorenz_income_curve(step)
    
    fig, ax = plt.subplots(1, 2, figsize=(8, 3))
    
    # Income distribution histogram
    ax[0].hist(income_data, bins=30, density=True, alpha=0.7, color="blue")
    ax[0].set_xlabel("Income")
    ax[0].set_ylabel("Density")
    ax[0].set_title(f"Income Distribution at Step {step}")
    
    # Lorenz curve for income
    ax[1].plot(pop_share, cum_income, label="Lorenz Curve", color="blue")
    ax[1].plot([0, 1], [0, 1], linestyle="--", color="gray", label="Perfect Equality")
    ax[1].set_xlabel("Population Share")
    ax[1].set_ylabel("Cumulative Income Share")
    ax[1].set_title(f"Lorenz Curve of Income at Step {step}")
    ax[1].legend()
    ax[1].grid(True)
    
    plt.tight_layout()
    plt.show()
