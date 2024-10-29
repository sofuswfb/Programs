# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 15:02:00 2024
Flytter resultater 

@author: User
"""

import os
import shutil

def gather_xlsx_files(source_root, target_folder):
    # Create the target folder if it doesn't exist
    os.makedirs(target_folder, exist_ok=True)
    
    # Walk through all folders in the source root
    for root, dirs, files in os.walk(source_root):
        for dir_name in dirs:
            folder_path = os.path.join(root, dir_name)
            xlsx_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]
            
            # If there are any xlsx files, process them
            if xlsx_files:
                for xlsx_file in xlsx_files:
                    source_file_path = os.path.join(folder_path, xlsx_file)
                    target_file_name = f"{dir_name}.xlsx"
                    target_file_path = os.path.join(target_folder, target_file_name)
                    
                    # Move and rename the file
                    shutil.move(source_file_path, target_file_path)
                    print(f"Moved {source_file_path} to {target_file_path}")
            else:
                print(f"No xlsx file found in {folder_path}, skipping...")

# Example usage
source_root = 'C:/Users/User/Desktop/Andreas script - Data folder/Andreas script - Data folder/Your cell data/Imprints(PCmedTI)'  # Replace with the path to the source root
target_folder = 'C:/Users/User/Desktop/Andreas script - Data folder/Andreas script - Data folder/Your cell data/Imprints(PCmedTI) resultater'  # Replace with the path to the target folder
gather_xlsx_files(source_root, target_folder)



 #%%
#%% Collecter dem i samlet excel fil
import os
import pandas as pd

def extract_count_columns_from_files(source_folder, target_folder, days, samples):
    # Create the target folder if it doesn't exist
    os.makedirs(target_folder, exist_ok=True)

    # Dictionary to hold the extracted data grouped by day
    grouped_data = {}

    # Iterate through each file in the source folder
    for file_name in os.listdir(source_folder):
        if file_name.endswith('.xlsx'):
            try:
                parts = file_name.split('_')
                # Extract day (from "dag X") and sample number (from "sample X")
                day = int(parts[2])  # Extract day number from parts[2]
                sample = int(parts[4])  # Extract sample number from parts[4]
            except (IndexError, ValueError):
                print(f"Filename {file_name} does not match the expected pattern, skipping...")
                continue

            if day in days and sample in samples:
                file_path = os.path.join(source_folder, file_name)
                print(f"Processing file: {file_path}")

                # Read the Excel file, skipping the first row
                df = pd.read_excel(file_path, skiprows=[0], header=None)

                # Assuming the first column is 'Sample' and the second column is 'Count'
                sample_column = df.iloc[:, 0]
                count_column = df.iloc[:, 1]
                column_name = f"Sample{sample}"
                
                # Create a key for grouping
                key = day
                
                if key not in grouped_data:
                    grouped_data[key] = pd.DataFrame()
                    grouped_data[key]['Sample'] = sample_column
                
                grouped_data[key][column_name] = count_column
            else:
                print(f"Filename {file_name} does not match the expected day or sample values, skipping...")

    # Save combined data for each group (by day)
    for day, combined_df in grouped_data.items():
        target_file = os.path.join(target_folder, f"Dag_{day}_combined.xlsx")
        combined_df.to_excel(target_file, index=False)
        print(f"Combined data for {day} saved to {target_file}")

# Example usage
source_folder = 'C:/Users/User/Desktop/Andreas script - Data folder/Andreas script - Data folder/Your cell data/Imprints(PCmedTI) resultater'  # Replace with the path to the source folder
target_folder = 'C:/Users/User/Desktop/Andreas script - Data folder/Andreas script - Data folder/Your cell data/Imprints(PCmedTI) resultater'  # Replace with the path to the target folder

# Lists of valid values
days = [1, 3, 5]
samples = [1, 2, 3]

# Now correctly passing both days and samples to the function
extract_count_columns_from_files(source_folder, target_folder, days, samples)




#%% Collecter dem i samlet excel fil for PC samples
import os
import pandas as pd

def extract_count_columns_from_files(source_folder, target_folder, days, nms, samples):
    # Create the target folder if it doesn't exist
    os.makedirs(target_folder, exist_ok=True)

    # Dictionary to hold the extracted data grouped by (#day, #nm)
    grouped_data = {}

    # Iterate through each file in the source folder
    for file_name in os.listdir(source_folder):
        if file_name.endswith('.xlsx'):
            try:
                parts = file_name.split('_')
                day = int(parts[2].replace('day', ''))
                sample = int(parts[5].replace('sample', '').replace('.xlsx', ''))
            except (IndexError, ValueError):
                print(f"Filename {file_name} does not match the expected pattern, skipping...")
                continue

            if day in days and nm in nms and sample in samples:
                file_path = os.path.join(source_folder, file_name)
                print(f"Processing file: {file_path}")

                # Read the Excel file, skipping the first row
                df = pd.read_excel(file_path, skiprows=[0], header=None)

                # Assuming the first column is 'Sample' and the second column is 'Count'
                sample_column = df.iloc[:, 0]
                count_column = df.iloc[:, 1]
                column_name = f"Sample{sample}"
                
                # Create a key for grouping
                key = (day, nm)
                
                if key not in grouped_data:
                    grouped_data[key] = pd.DataFrame()
                    grouped_data[key]['Sample'] = sample_column
                
                grouped_data[key][column_name] = count_column
            else:
                print(f"Filename {file_name} does not match the expected day, nm, or sample values, skipping...")

    # Save combined data for each group (#day, #nm)
    for (day, nm), combined_df in grouped_data.items():
        target_file = os.path.join(target_folder, f"PC_{day}day_nominUV_{nm}nm.xlsx")
        combined_df.to_excel(target_file, index=False)
        print(f"Combined data for {day}day  saved to {target_file}")

# Example usage
source_folder = 'C:/Users/User/Desktop/Andreas script - Data folder/Andreas script - Data folder/Your cell data/Imprints(PCmedTI) resultater'  # Replace with the path to the source folder
target_folder = 'C:/Users/User/Desktop/Andreas script - Data folder/Andreas script - Data folder/Your cell data/Imprints(PCmedTI) resultater'  # Replace with the path to the target folder

# Lists of valid values
days = [1, 3, 5]
nms = [500, 2500]
samples = [1, 2, 3]

extract_count_columns_from_files(source_folder, target_folder, days, samples)
