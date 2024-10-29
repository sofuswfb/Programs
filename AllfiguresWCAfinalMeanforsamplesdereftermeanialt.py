import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
from itertools import combinations
from uncertainties import ufloat
from uncertainties.umath import *  # This allows for mathematical operations on ufloats

# Function to add statistical annotation
def add_stat_annotation(ax, p_val, x1, x2, y, h, significance_thresholds, already_annotated):
    if p_val < significance_thresholds[0]:
        stars = "***"
    elif p_val < significance_thresholds[1]:
        stars = "**"
    elif p_val < significance_thresholds[2]:
        stars = "*"
    else:
        stars = "ns"  # Not significant

    if stars != "ns" and (x1, x2) not in already_annotated and (x2, x1) not in already_annotated:
        # Only add line and stars if not already annotated for this comparison
        ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, color='black')  # Add horizontal line
        ax.text((x1 + x2) * 0.5, y + h, stars, ha='center', va='bottom', color='black')  # Add stars
        already_annotated.add((x1, x2))  # Mark this comparison as annotated
        return True  # Return True if a significance annotation is added
    return False  # Return False if no annotation is added

# Define significance thresholds
significance_thresholds = [0.001, 0.01, 0.05]

#file_paths = [
   # r'C:\Users\User\Desktop\Master\PMMA\Water Contact angle\WCA PMMA 0 minUV 2105.xlsx',
   # r'C:\Users\User\Desktop\Master\PMMA\Water Contact angle\WCA PMMA 5 minUV 2105.xlsx',
   # r'C:\Users\User\Desktop\Master\PMMA\Water Contact angle\WCA PMMA 10 minUV 2105.xlsx'
#]
#file_paths = [
   # r'C:\Users\User\Desktop\Master\Polycarbonate\Water contact angle\WCA PC 2105 0minUV.xlsx',
   # r'C:\Users\User\Desktop\Master\Polycarbonate\Water contact angle\WCA PC 2105 5minUV.xlsx',
  #  r'C:\Users\User\Desktop\Master\Polycarbonate\Water contact angle\WCA PC 2105 10minUV.xlsx'
#]
file_paths = [
    r'C:\Users\User\Desktop\Master\PMMA\Water Contact angle\WCA PMMA 0 minUV 1604.xlsx',
    r'C:\Users\User\Desktop\Master\PMMA\Water Contact angle\WCA PMMA 16 minUV 1604 turned.xlsx',
    r'C:\Users\User\Desktop\Master\PMMA\Water Contact angle\WCA PMMA 16 minUV 1604 noturned.xlsx'
]
custom_labels = [
    'UV Exposure - 0 min',
    'UV Exposure - 16 min turned',
    'UV Exposure - 16 min noturn'
]

# Initialize lists to store the results
all_values = []
all_errors = []
all_labels = []
all_data = []  # To store the raw data for t-tests, including the differences

# Loop through each file
for i, file_path in enumerate(file_paths):
    
    # Load the data, only columns B-F (which corresponds to Excel columns 1 to 5, since it's 0-indexed)
    data = pd.read_excel(file_path, skiprows=2, usecols='B:F')

    
    # Extract columns Mean_adv, Mean_rec, std_adv, std_rec
    data_clean = data[['Mean_adv', 'mean_rec', 'std_ adv', 'std_rec', 'diff']].dropna()
    # Rename columns for consistency
    data_clean.columns = ['Mean_adv', 'Mean_rec', 'Std_ adv', 'Std_rec','diff']
    all_data.append(data_clean[['Mean_adv', 'Mean_rec', 'diff']].values)
    # Create ufloat values for each individual row (advancing and receding angles with uncertainties)
    ufloat_adv = [ufloat(row['Mean_adv'], row['Std_ adv']) for _, row in data_clean.iterrows()]
    ufloat_rec = [ufloat(row['Mean_rec'], row['Std_rec']) for _, row in data_clean.iterrows()]

    # Calculate the mean of the ufloat values (this will propagate the uncertainties)
    mean_adv = sum(ufloat_adv) / len(ufloat_adv)
    mean_rec = sum(ufloat_rec) / len(ufloat_rec)
    
    #print(mean_rec)
    # Calculate the difference between the means
    mean_diff = mean_adv - mean_rec

    # Store the nominal values and uncertainties separately for plotting
    values = [mean_adv.nominal_value, mean_rec.nominal_value, mean_diff.nominal_value]
    errors = [mean_adv.std_dev, mean_rec.std_dev, mean_diff.std_dev]
    
    all_values.append(values)
    all_errors.append(errors)
    all_labels.append(custom_labels[i])  # Use custom label
# print(all_values)
# print(all_errors)    
# print(all_labels)
# print(all_data)
# Plot the results for all sheets
x = np.arange(len(['Mean Advancing Angle', 'Mean Receding Angle', 'Difference']))  # label locations
width = 0.2  # the width of the bars

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Plot bars for each dataset
for i in range(len(file_paths)):
    ax.bar(x + i*width, all_values[i], width, yerr=all_errors[i], capsize=5, label=all_labels[i])

# Add labels, title, and legend with customized font sizes
ax.set_ylabel('Angle (degrees)', fontsize=16)

# Shift the x-tick positions to center them under the bars
ax.set_xticks(x + width)  # Shift by half the width

ax.set_xticklabels(['Mean Advancing Angle', 'Mean Receding Angle', 'Difference'], fontsize=16)
ax.tick_params(axis='y', labelsize=16)
ax.legend(fontsize=12)

# Perform t-tests for the UV exposure comparisons within each category (advancing, receding, difference)
comparisons = list(combinations(range(len(file_paths)), 2))
y_base_offset = 12  # Initial y offset for placing significance marks above the bars

# Set to track already annotated comparisons to avoid duplicates
already_annotated = set()

# Loop through each category (advancing, receding, difference)
for i, label in enumerate(['Mean Advancing Angle', 'Mean Receding Angle', 'diff']):
    # Get the maximum y-value (for the highest bar) in this category for setting the base y-offset
    y_max = np.max([all_values[j][i] for j in range(len(all_values))]) + y_base_offset

    # Loop through each pairwise comparison of UV exposure groups within the current category
    for idx, comp in enumerate(comparisons):
        j, k = comp
        label_j = custom_labels[j]
        label_k = custom_labels[k]
        
        # Height of the significance line
        h = 3  # Adjust the height if necessary

        # Perform t-tests for each UV exposure group within each category
        t_stat, p_val = ttest_ind(all_data[j][:, i], all_data[k][:, i])

        # Print the p-values for each comparison
       # print(f"P-value for comparison between {label_j} and {label_k} in {label}: {p_val:.4f}")

        # Try to add the statistical annotation for this comparison
        if add_stat_annotation(ax, p_val, x[i] + j*width, x[i] + k*width, y_max, h, significance_thresholds, already_annotated):
            y_max += h + 5  # Increase the y position for the next annotation if an annotation is drawn

# Show the plot
plt.show()
