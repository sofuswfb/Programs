import os
import pandas as pd
import matplotlib.pyplot as plt

def calculate_global_y_limits(source_folder, days, selected_samples=None):
    """
    Calculate global y-axis limits across all relevant Excel files for consistent plotting.

    Parameters:
        source_folder (str): Path to the folder containing Excel files.
        days (list of int): List of day values to filter the files.
        selected_samples (list of str, optional): List of sample names to include. Defaults to None, meaning all samples are included.

    Returns:
        dict: Dictionary with day as keys and (min, max) tuples as values for y-axis limits.
    """
    y_limits = {day: (float('inf'), float('-inf')) for day in days}

    for file_name in os.listdir(source_folder):
        if file_name.endswith('.xlsx'):
            try:
                day = extract_day_from_filename(file_name)
            except ValueError:
                print(f"Skipping file due to naming issues: {file_name}")
                continue

            if day in days:
                file_path = os.path.join(source_folder, file_name)
                df = pd.read_excel(file_path)

                # Filter rows based on selected samples, if provided
                if selected_samples:
                    df = filter_samples(df, selected_samples)

                if not df.empty:
                    update_y_limits(y_limits, day, df)

    return y_limits

def extract_day_from_filename(file_name):
    """
    Extract the day number from the filename.

    Parameters:
        file_name (str): The filename from which to extract the day.

    Returns:
        int: The extracted day number.
    
    Raises:
        ValueError: If the filename format is incorrect.
    """
    try:
        parts = file_name.split('_')
        return int(parts[1].replace('day', ''))
    except (IndexError, ValueError) as e:
        raise ValueError(f"Filename does not match expected pattern: {file_name}") from e

def filter_samples(df, selected_samples):
    """
    Filter the DataFrame to include only the specified samples.

    Parameters:
        df (pd.DataFrame): The DataFrame to filter.
        selected_samples (list of str): List of sample names to include.

    Returns:
        pd.DataFrame: The filtered or original DataFrame.
    """
    if not selected_samples:  # If selected_samples is None or empty, return the original DataFrame
        return df

    filtered_df = df[df.iloc[:, 0].isin(selected_samples)]
    if filtered_df.empty:
        print("No matching samples found after filtering.")
    return filtered_df

def update_y_limits(y_limits, day, df):
    """
    Update the global y-axis limits for the given day based on the data.

    Parameters:
        y_limits (dict): The current y_limits dictionary to update.
        day (int): The day corresponding to the current data.
        df (pd.DataFrame): The DataFrame containing the data to evaluate.
    """
    count_data = df.iloc[:, 1:]
    min_count = count_data.min().min()
    max_count = count_data.max().max()

    current_min, current_max = y_limits[day]
    y_limits[day] = (min(current_min, min_count), max(current_max, max_count))

def plot_excel_files(source_folder, days, nms, selected_samples=None):
    """
    Process Excel files and generate plots for specified days, nm values, and samples.

    Parameters:
        source_folder (str): Path to the folder containing Excel files.
        days (list of int): List of day values to filter files.
        nms (list of int): List of nm values to filter files.
        selected_samples (list of str, optional): List of sample names to include. Defaults to None.
    """
    y_limits = calculate_global_y_limits(source_folder, days, selected_samples)

    for file_name in os.listdir(source_folder):
        if file_name.endswith('.xlsx'):
            try:
                day, nm = extract_day_and_nm_from_filename(file_name)
            except ValueError:
                print(f"Skipping file due to naming issues: {file_name}")
                continue

            if day in days and nm in nms:
                file_path = os.path.join(source_folder, file_name)
                print(f"Processing file: {file_path}")
                df = pd.read_excel(file_path)

                if selected_samples:
                    df = filter_samples(df, selected_samples)

                if not df.empty:
                    plot_data(df, day, nm, y_limits[day])

def extract_day_and_nm_from_filename(file_name):
    """
    Extract the day and nm values from the filename.

    Parameters:
        file_name (str): The filename from which to extract the day and nm values.

    Returns:
        tuple: A tuple containing the extracted day and nm values as integers.
    
    Raises:
        ValueError: If the filename format is incorrect.
    """
    try:
        parts = file_name.split('_')
        day = int(parts[1].replace('day', ''))
        nm = int(parts[3].replace('nm', '').replace('.xlsx', ''))
        return day, nm
    except (IndexError, ValueError) as e:
        raise ValueError(f"Filename does not match expected pattern: {file_name}") from e

def plot_data(df, day, nm, y_limits):
    """
    Plot the data for a specific day and nm value with special handling for 'C', 'E1', and 'E2'.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data to plot.
        day (int): The day corresponding to the current data.
        nm (int): The nm value corresponding to the current data.
        y_limits (tuple): The y-axis limits for the plot.
    """
    plt.figure(figsize=(7, 8))  # Start a new figure

    # Separate the special cases
    c_rows = df[df['Sample'] == 'C']
    e1_rows = df[df['Sample'].str.contains('E1')]
    e2_rows = df[df['Sample'].str.contains('E2')]
    
    # Aggregate 'C' rows by taking the mean across them
    if not c_rows.empty:
        c_mean = c_rows.iloc[:, 1:].mean().mean()
        c_std = c_rows.iloc[:, 1:].std().mean()  # Standard deviation across 'C' rows
        plt.errorbar('C', c_mean, yerr=c_std, fmt='o', capsize=5, label='C')

    # Plot each 'E1' and 'E2' row individually
    for index, row in e1_rows.iterrows():
        e1_mean = row[1:].mean()
        e1_std = row[1:].std()
        plt.errorbar(f'E1_{index}', e1_mean, yerr=e1_std, fmt='o', capsize=5, label=f'E1_{index}')
    
    for index, row in e2_rows.iterrows():
        e2_mean = row[1:].mean()
        e2_std = row[1:].std()
        plt.errorbar(f'E2_{index}', e2_mean, yerr=e2_std, fmt='o', capsize=5, label=f'E2_{index}')
    
    # Plot all other samples
    other_samples = df[~df['Sample'].str.contains('C|E1|E2')]
    for _, row in other_samples.iterrows():
        sample = row['Sample']
        mean_value = row[1:].mean()
        std_dev = row[1:].std()
        plt.errorbar(sample, mean_value, yerr=std_dev, fmt='o', capsize=5, label=sample)
    
    # Finalize the plot
    plt.title(f"PC {day} Day - {nm}nm")
    plt.xlabel('Sample')
    plt.ylabel('Count')
    plt.xticks(rotation=90)
    plt.ylim(y_limits[0] * 0.95, y_limits[1] * 1.05)  # Add 5% padding to y-limits
    plt.grid(True)
    #plt.legend()
    plt.tight_layout()
    plt.show()

# Example usage
if __name__ == "__main__":
    source_folder = r'C:\Users\User\Desktop\Andreas script - Data folder\Andreas script - Data folder\Your cell data\Imprints(PCmedTI) resultater\Combined data'
    
    # Lists of valid values
    days = [1, 3, 5]
    nms = [500, 2500]
    
    # Define the samples you want to include
    #selected_samples = []
    selected_samples = ['1;2 (HEX)', '0.5;2 (HEX)', '1;0.5 (HEX)', '2;0.3 (HEX)', 'C']  # Replace with your actual sample names

    plot_excel_files(source_folder, days, nms, selected_samples)
