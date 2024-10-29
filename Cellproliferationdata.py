import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Function to read CSV file and calculate particle count statistics
def calculate_particle_stats(folder_path, folder_name):
    # Find the CSV files in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    stats = []

    for csv_file in csv_files:
        file_path = os.path.join(folder_path, csv_file)
        df = pd.read_csv(file_path)
        
        # Calculate mean, standard deviation, and sample size for particle count
        mean_particle_count = df['Particle Count'].mean()
        std_particle_count = df['Particle Count'].std() if len(df['Particle Count']) > 1 else 0
        sample_size = len(df['Particle Count'])
        
        # Append the result with folder name
        stats.append((folder_name, mean_particle_count, std_particle_count, sample_size))
    
    return stats

# Function to traverse through multiple folders and gather results
def gather_folder_results(base_directory):
    folder_stats = []
    
    # Traverse through the directories
    for folder_name in os.listdir(base_directory):
        folder_path = os.path.join(base_directory, folder_name)
        if os.path.isdir(folder_path):
            # Get particle count statistics using only the folder name (last folder)
            folder_stats += calculate_particle_stats(folder_path, folder_name)
    
    return folder_stats

# Function to plot the results with custom sorting and pillars (bars)
def plot_results_enhanced(folder_stats, custom_order=None, title="Mean Particle Count per 1 cm^2", ymin=None, ymax=None):
    # Sort folder_stats based on custom_order if provided
    if custom_order:
        folder_stats = sorted(folder_stats, key=lambda x: custom_order.index(x[0]) if x[0] in custom_order else len(custom_order))
    
    folder_names = [stat[0] for stat in folder_stats]  # Only folder name
    
    # Divider with 4 here
    means = [stat[1] for stat in folder_stats]
    stds = [stat[2] for stat in folder_stats]
    
    plt.figure(figsize=(6, 6))
    
    # Create the bar plot with error bars
    bars = plt.bar(folder_names, means, yerr=stds, capsize=7, color='skyblue', edgecolor='black', label='Mean Particle Count')
    
    # Adding grid, axis labels, and a larger title
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.ylabel('Cells/$cm^2$', fontsize=14)
    plt.title(title, fontsize=14)
    
    # Set y-axis limits if provided
    if ymin is not None and ymax is not None:
        plt.ylim(ymin, ymax)
    
    # Add a grid for better readability
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')

    plt.tight_layout()
    plt.show()

# Function to print the results in a readable table format before plotting
def print_stats_table(folder_stats):
    print("\nParticle Count Statistics:")
    print(f"{'Sample':<20}{'Mean Particle Count':<20}{'Std Dev':<20}{'Sample Size':<15}")
    print("-" * 75)
    for folder_name, mean, std, sample_size in folder_stats:
        print(f"{folder_name:<20}{mean:<20.2f}{std:<20.2f}{sample_size:<15}")
    print("-" * 75)

# Example usage (provide the base directory with folders):
#Ti experiment 2    
#base_directory = r"C:\Users\User\Desktop\Master\Titanium\proliferation\Flade\Forsøg 2\Ti UV billeder"
#Ti experiment 1
base_directory = r"C:\Users\User\Desktop\Master\Titanium\proliferation\Flade\Forsøg 1\Resultater"
#PMMA experiment 10min UV
#base_directory = r"C:\Users\User\Desktop\Master\PMMA\Proliferation\flade\PMMA UV Billeder\10min UV behandling (2_5 og 6_5)"

#PMMA experiment 2
#base_directory = r"C:\Users\User\Desktop\Master\PMMA\Proliferation\flade\PMMA UV Billeder\UV behandling(01_03 og 7_3)/sorteret dage og derefter min/6 day"
#PC resultater
#base_directory = r"C:\Users\User\Desktop\Master\Polycarbonate\Proliferation\Flade\Kun UV"

folder_stats = gather_folder_results(base_directory)

# Define custom order for the folder names
custom_order = ['1 day 0min', '1 day 5min', '1 day 10min','4 day 0min', '4 day 5min', '4 day 10min', '6 day 0min', '6 day 5min', '6 day 10min']  # You can modify this to your desired order
custom_order = ['0 min', '5 min', '10 min']

# Print the results in a table format before plotting
print_stats_table(folder_stats)

# Plot the results with enhanced plotting
plot_results_enhanced(folder_stats, custom_order=custom_order, title="Mean Cell Count on PMMA per cm$^2$ day 1")
