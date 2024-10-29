# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 00:50:31 2024

@author: User
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
from itertools import combinations

# Set larger font sizes for all plot elements
plt.rcParams.update({
    'font.size': 14,  # General font size
    'axes.titlesize': 20,  # Title font size
    'axes.labelsize': 18,  # X and Y label font size
    'xtick.labelsize': 16,  # X tick label size
    'ytick.labelsize': 16,  # Y tick label size
    'legend.fontsize': 14,  # Legend font size
    'figure.titlesize': 24  # Figure title size
})

# Load the Excel file
file_path = r'C:\Users\User\Desktop\Master\Polycarbonate\PCR\PCRMaster.xlsx'  # Replace with your actual file path
df = pd.read_excel(file_path, sheet_name='Ark1')

# Clean up the dataframe to focus on relevant columns
df_cleaned = df[['Time', 'Sample', 'ValueAlpL', 'ValueRUNX2']].copy()

# Group by 'Sample' and 'Time' to calculate the mean and standard deviation for 'AlpL' and 'RunX2'
grouped = df_cleaned.groupby(['Sample', 'Time']).agg(
    AlpL_mean=('ValueAlpL', 'mean'),
    AlpL_std=('ValueAlpL', 'std'),
    RunX2_mean=('ValueRUNX2', 'mean'),
    RunX2_std=('ValueRUNX2', 'std')
).reset_index()

# Define colors for each time point
color_map = {3: '#00FFB5', 5: '#32CD32', 7: '#006400'}

# Function to perform pairwise t-tests for all combinations of samples for a given time point
def perform_pairwise_ttests(data, time_point, value_column):
    # Filter data for the current time point
    df_time = data[data['Time'] == time_point]
    
    # Perform t-tests for every combination of samples
    ttest_results = {}
    sample_combinations = list(combinations(df_time['Sample'].unique(), 2))  # All possible combinations of two samples
    
    for (sample1, sample2) in sample_combinations:
        sample1_values = df_time[df_time['Sample'] == sample1][value_column].dropna()
        sample2_values = df_time[df_time['Sample'] == sample2][value_column].dropna()
        t_stat, p_value = ttest_ind(sample1_values, sample2_values)
        ttest_results[(sample1, sample2)] = p_value
    
    return ttest_results

# Function to add significance bars to the plot
def add_significance_bar(ax, x1, x2, y, h, p_value, level):
    bar_x = [x1, x1, x2, x2]
    bar_y = [y + h * level, y + h * (level + 0.75), y + h * (level + 0.75), y + h * level]  # Adjust bar height based on level
    ax.plot(bar_x, bar_y, lw=1.5, color='black')

    # Determine significance level
    if p_value < 0.01:
        significance = '**'
    elif p_value < 0.05:
        significance = '*'
    else:
        return  # No need to add anything if p-value is not significant

    ax.text((x1 + x2) * 0.5, y + h * (level + 0.75), significance, ha='center', va='bottom', color='black')

# Function to plot bar chart for a given time point
def plot_barchart_for_time(data, time_point, value_column, error_column, title, ttest_results, samples):
    # Filter data for the given time point
    df_time = data[data['Time'] == time_point]

    # Create the bar chart with specific colors
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(samples, df_time[value_column], yerr=df_time[error_column], 
                  capsize=5, color=color_map[time_point])
    ax.set_title(f'{title} day {time_point}')
    ax.set_xlabel('Sample')
    ax.set_ylabel(f'{title} Mean')
    ax.set_xticks(range(len(samples)))
    ax.set_xticklabels(samples, rotation=45)

    # Set a larger y-axis limit to make space for significance bars
    ymin = 0
    ymax = df_time[value_column].max() * 2
    ax.set_ylim([ymin, ymax])  # Set the y-axis limits slightly beyond the min/max values

    # Add p-values from t-test and significance bars for every pairwise comparison
    level = 0  # This keeps track of the level for stacking multiple bars
    sample_indices = {sample: idx for idx, sample in enumerate(samples)}  # Map sample names to bar positions
    for (sample1, sample2), p_value in ttest_results.items():
        if p_value < 0.05:
            x1, x2 = sample_indices[sample1], sample_indices[sample2]
            y = max(df_time[value_column].iloc[x1] + df_time[error_column].iloc[x1], 
                    df_time[value_column].iloc[x2] + df_time[error_column].iloc[x2]) + 0.03 * ymax
            add_significance_bar(ax, x1, x2, y, 0.04 * ymax, p_value, level)
            level += 3  # Increment level to stack bars

    plt.tight_layout()
    plt.savefig(f'C:/Users/User/Desktop/Master/Polycarbonate/PCR/{title}_Time_{time_point}.png')
    plt.show()

# Define the control sample (Flat control)
control_sample = 'Flat control'

# Plot for AlpL at time points 3, 5, and 7 and perform pairwise t-tests
for time in [3, 5, 7]:
    samples = grouped['Sample'].unique()
    ttest_results_alpl = perform_pairwise_ttests(df, time, 'ValueAlpL')
    plot_barchart_for_time(grouped, time, 'AlpL_mean', 'AlpL_std', 'AlpL', ttest_results_alpl, samples)

# Plot for RUNX2 at time points 3, 5, and 7 and perform pairwise t-tests
for time in [3, 5, 7]:
    samples = grouped['Sample'].unique()
    ttest_results_runx2 = perform_pairwise_ttests(df, time, 'ValueRUNX2')
    plot_barchart_for_time(grouped, time, 'RunX2_mean', 'RunX2_std', 'RUNX2', ttest_results_runx2, samples)
