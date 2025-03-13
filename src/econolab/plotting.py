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
