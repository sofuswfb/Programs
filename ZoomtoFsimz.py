# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 00:30:23 2024

@author: User
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import re
import random
import numpy as np  # Import numpy for area calculation

# Load the data from the file
file_path = r'C:\Users\User\Desktop\Master\Polycarbonate\ToF-SIMS\noUVneg\PC_NoUV_Spot1_neg_Bi3++_0.txt'  # Adjust the file path if necessary
excel_file_path = r'C:\Users\User\Desktop\Master\Polycarbonate\ToF-SIMS\noUVneg\Excel\PC_NoUV_Spot1_neg_Bi3++.xls'  # For .xls or .xlsx files

# Read the plot data (mass spectrum data)
data = pd.read_csv(file_path, sep="\t", skiprows=3, names=["Channel", "Mass (u)", "Intensity"])

# Read the peak assignment data from the Excel file
peaks = pd.read_excel(excel_file_path)  # Use read_excel to load .xls or .xlsx files

# Drop any rows where 'Mass (u)' or 'Intensity' might be missing or have invalid data
data = data.dropna()

# Convert columns to numeric, coercing errors
data['Mass (u)'] = pd.to_numeric(data['Mass (u)'], errors='coerce')
data['Intensity'] = pd.to_numeric(data['Intensity'], errors='coerce')
data = data.dropna()

# Define the interval for the Mass (u) values to be plotted
mass_min_limit = 58# Example: Minimum value of Mass (u) to be plotted
mass_max_limit = 60 # Example: Maximum value of Mass (u) to be plotted

# Filter the data to only include the given interval
subset = data[(data['Mass (u)'] >= mass_min_limit) & (data['Mass (u)'] <= mass_max_limit)]

# Function to format chemical labels using LaTeX-style, excluding the minus sign at the end
def format_label(assignment):
    # Remove the minus sign at the end, if present
    assignment = assignment.rstrip('-')
    # Replace underscores followed by numbers with LaTeX subscript format
    formatted_label = re.sub(r'_(\d+)', r'$_{\1}$', assignment)
    return formatted_label

# Function to generate random colors
def get_random_color():
    return "#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])

# Create the plot
plt.figure(figsize=(10, 6))

# Plot the data within the given interval
plt.plot(subset['Mass (u)'], subset['Intensity'], color='blue', linewidth=0.5)

# Get the current y-axis limits to set a consistent arrow length
_, y_max = plt.ylim()

# Increase the y-axis limit by 20% to make room for the arrows and labels
plt.ylim(0, y_max * 1.3)

# Set a fixed arrow length based on the new y-axis range
arrow_length = y_max * 0.15  # 15% of the original y-axis height

# Variable to alternate label height to avoid overlap
alternate_height = True

# Dictionary to store the areas of the peaks
peak_areas = {}

# Highlight the areas and label the peaks based on the Excel data
for i, peak in peaks.iterrows():
    lower_mass = peak['Lower Mass (u)']
    upper_mass = peak['Upper Mass (u)']
    center_mass = peak['Center Mass (u)']
    assignment = format_label(peak['Assignment'])  # Format the label
    color = get_random_color()  # Get a random color for each peak
    
    # Only process peaks within the specified mass range
    if lower_mass >= mass_min_limit and upper_mass <= mass_max_limit:
        # Highlight the area under the peak with a random color
        area_data = subset[(subset['Mass (u)'] >= lower_mass) & (subset['Mass (u)'] <= upper_mass)]
        
        # Get the peak intensity for the current peak
        peak_intensity = area_data['Intensity'].max()
        
        # Fill the area under the peak
        plt.fill_between(area_data['Mass (u)'], area_data['Intensity'], color=color, alpha=0.5)

        # Calculate the area under the peak using the trapezoidal rule
        area = np.trapz(area_data['Intensity'], area_data['Mass (u)'])
        peak_areas[assignment] = area  # Store the area with the peak label

        # Stagger the labels to avoid overlap
        label_y_position = peak_intensity + (arrow_length if alternate_height else arrow_length * 1.5)
        alternate_height = not alternate_height  # Switch the height for the next label

        # Add an arrow with the label pointing to the peak, with a consistent arrow length
        plt.annotate(assignment, xy=(center_mass, peak_intensity), xytext=(center_mass, label_y_position),
                     arrowprops=dict(facecolor='black', arrowstyle='->'),
                     horizontalalignment='center', verticalalignment='bottom', fontsize=14)  # Adjust fontsize here

# Set the title and labels
plt.title('Polycarbonate UV/O3 negative Bias')
plt.xlabel('Mass (u)')
plt.ylabel('Intensity')

# Set the x-axis limits to the exact data range to avoid empty spaces
plt.xlim([subset['Mass (u)'].min(), subset['Mass (u)'].max()])

# Format the y-axis to scientific notation
ax = plt.gca()
ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

# Add grid
plt.grid(True)

# Show the plot
plt.tight_layout()
plt.show()

# Print the calculated areas for each peak
for peak_label, area in peak_areas.items():
    print(f"Peak {peak_label}: Area = {area}")
