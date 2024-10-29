import pandas as pd
import matplotlib.pyplot as plt
import os
import re  # Import regex module for formatting the labels
from scipy.stats import ttest_ind  # Import for performing t-test

# Function to load CSV or Excel file based on the file extension
def load_file(file_path):
    file_ext = os.path.splitext(file_path)[1]
    if file_ext == '.csv':
        data = pd.read_csv(file_path)
    elif file_ext in ['.xls', '.xlsx']:
        data = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format: {}".format(file_ext))
    return data

# Function to find the closest peaks to given mass values
def find_closest_peaks(data, target_masses):
    closest_peaks = []
    for target in target_masses:
        # Find the row where 'Center Mass (u)' is closest to the target mass
        closest_row = data.iloc[(data['Center Mass (u)'] - target).abs().argsort()[:1]]
        closest_peaks.append(closest_row)
    # Concatenate the results into a single DataFrame
    return pd.concat(closest_peaks)

# Function to format the assignment label using subscripts
def format_assignment(assignment):
    # Apply regex to replace _digit with subscript formatting (e.g., CH_3 -> CH₃)
    formatted_label = re.sub(r'_(\d+)', r'$_{\1}$', assignment)
    return formatted_label

# Function to extract the areas and assignments at user-specified mass values
def extract_peak_areas(file_path, target_masses):
    data = load_file(file_path)
    # Find the closest peaks to the user-defined mass values
    peaks = find_closest_peaks(data, target_masses)
    # Return the 'Center Mass (u)', 'Area', and 'Assignment' columns
    return peaks[['Center Mass (u)', 'Area', 'Assignment']]

# Function to calculate the area ratio between two peaks for each sample
def calculate_sample_area_ratio(data, mass_1, mass_2):
    if len(data) == 2:  # Ensure we have two peaks (mass_1 and mass_2)
        peak_1 = data.loc[data['Center Mass (u)'].sub(mass_1).abs().idxmin()]
        peak_2 = data.loc[data['Center Mass (u)'].sub(mass_2).abs().idxmin()]
        ratio = peak_1['Area'] / peak_2['Area']
        # Format the assignments using the provided regex
        formatted_assignment_1 = format_assignment(peak_1['Assignment'])
        formatted_assignment_2 = format_assignment(peak_2['Assignment'])
        return ratio, formatted_assignment_1, formatted_assignment_2
    else:
        return None, None, None

# Function to process and calculate the area ratios for all files in a folder
def process_folder(folder, mass_1, mass_2):
    file_ratios = []
    assignments = []

    # List all files in the folder
    files = sorted([f for f in os.listdir(folder) if f.endswith(('.xls', '.xlsx', '.csv'))])
    
    # Loop through each file and calculate area ratio
    for file in files:
        file_path = os.path.join(folder, file)
        data = extract_peak_areas(file_path, [mass_1, mass_2])
        
        ratio, assignment_1, assignment_2 = calculate_sample_area_ratio(data, mass_1, mass_2)
        if ratio is not None:
            file_ratios.append(ratio)
            assignments.append((assignment_1, assignment_2))

    return file_ratios, assignments

# Function to calculate average and standard deviation
def calculate_mean_std(ratios):
    mean = pd.Series(ratios).mean()
    std = pd.Series(ratios).std()
    return mean, std

# Function to perform Student's t-test and return p-value
def perform_ttest(no_uv_ratios, uv_ratios):
    t_stat, p_value = ttest_ind(no_uv_ratios, uv_ratios, equal_var=True)  # Student's t-test assuming equal variances
    return p_value

# Function to plot the average area ratios with standard deviations, peak assignments, and p-value in the title
def plot_noUV_vs_UV(no_uv_mean, no_uv_std, uv_mean, uv_std, no_uv_assignments, uv_assignments, p_value):
    labels = ['NoUV', 'UV']
    means = [no_uv_mean, uv_mean]
    stds = [no_uv_std, uv_std]

    plt.figure(figsize=(8, 6))
    
    # Create a bar plot with error bars (standard deviation)
    plt.bar(labels, means, yerr=stds, capsize=10, color=['orange', 'purple'], alpha=0.7)

    # Add formatted peak assignments to the title and show p-value
    plt.title(f'Average Area Ratios for NoUV/ozone vs UV/ozone\n'
              f'{no_uv_assignments[0]} / {no_uv_assignments[1]}\n'
              f'p-value = {p_value:.4f}', fontsize=14)

    # Add the y-axis label with the formatted assignment
    plt.ylabel(f'Area Ratio ({no_uv_assignments[0]} / {no_uv_assignments[1]})', fontsize=12)

    plt.tight_layout()
    plt.show()

# Function to process both NoUV and UV folders
def process_folders_and_plot(nouv_folder, uv_folder, mass_1, mass_2):
    # Process NoUV folder
    no_uv_ratios, no_uv_assignments = process_folder(nouv_folder, mass_1, mass_2)
    
    # Process UV folder
    uv_ratios, uv_assignments = process_folder(uv_folder, mass_1, mass_2)
    
    if not no_uv_ratios or not uv_ratios:
        print("No area ratios could be calculated. Check your files.")
        return

    # Calculate mean and std for NoUV and UV
    no_uv_mean, no_uv_std = calculate_mean_std(no_uv_ratios)
    uv_mean, uv_std = calculate_mean_std(uv_ratios)

    # Perform Student's t-test to get p-value
    p_value = perform_ttest(no_uv_ratios, uv_ratios)

    # Use the assignments from the first file to annotate the title and y-axis
    no_uv_assignments = no_uv_assignments[0] if no_uv_assignments else ('NoUV peak', 'NoUV peak')
    uv_assignments = uv_assignments[0] if uv_assignments else ('UV peak', 'UV peak')

    # Plot the averages with standard deviation, formatted assignments, and p-value
    plot_noUV_vs_UV(no_uv_mean, no_uv_std, uv_mean, uv_std, no_uv_assignments, uv_assignments, p_value)

# Example usage:
nouv_folder = r'C:\Users\User\Desktop\Master\Polycarbonate\ToF-SIMS\NoUVpos\Excel'  # Update with your actual NoUV folder
uv_folder = r'C:\Users\User\Desktop\Master\Polycarbonate\ToF-SIMS\UVpos\Excel'      # Update with your actual UV folder

# You can insert your own mass values here, e.g., 25 and 211
mass_1 = 55.1
mass_2 = 91

# Process both folders and plot the average area ratios with assignment labels in title, y-axis, and p-value
process_folders_and_plot(nouv_folder, uv_folder, mass_1, mass_2)
