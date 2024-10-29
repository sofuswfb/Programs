import os
import pandas as pd
import matplotlib.pyplot as plt

def calculate_separate_y_limits(source_folder, days, selected_samples=None):
    """
    Calculate separate y-axis limits for each day across all relevant Excel files.

    Parameters:
        source_folder (str): Path to the folder containing Excel files.
        days (list of int): List of day values to filter the files.
        selected_samples (list of str, optional): List of sample names to include. Defaults to None.

    Returns:
        dict: A dictionary with day as keys and (min, max) tuples as values for y-axis limits per day.
    """
    y_limits = {day: (float('inf'), float('-inf')) for day in days}

    for file_name in os.listdir(source_folder):
        if file_name.endswith('.xlsx') and 'combined' in file_name:  # Check if 'combined' is in the filename
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
                    # Calculate the min and max including the error bars for the specific day
                    for _, row in df.iterrows():
                        mean_value = row[1:].mean() / 4
                        std_dev = row[1:].std() / 4
                        y_min = mean_value - std_dev
                        y_max = mean_value + std_dev
                        current_min, current_max = y_limits[day]
                        y_limits[day] = (min(current_min, y_min), max(current_max, y_max))

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
        return int(parts[1])  # Extract day from parts[1]
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

def plot_excel_files(source_folder, days, selected_samples=None):
    """
    Process Excel files and generate plots for specified days and samples.

    Parameters:
        source_folder (str): Path to the folder containing Excel files.
        days (list of int): List of day values to filter files.
        selected_samples (list of str, optional): List of sample names to include. Defaults to None.
    """
    # Calculate separate y-axis limits for each day
    day_y_limits = calculate_separate_y_limits(source_folder, days, selected_samples)

    for file_name in os.listdir(source_folder):
        if file_name.endswith('.xlsx') and 'combined' in file_name:  # Only process files with 'combined' in the name
            try:
                day = extract_day_from_filename(file_name)
            except ValueError:
                print(f"Skipping file due to naming issues: {file_name}")
                continue

            if day in days:
                file_path = os.path.join(source_folder, file_name)
                print(f"Processing file: {file_path}")
                df = pd.read_excel(file_path)

                # Divide all cell count values by 4.41 before plotting
                df.iloc[:, 1:] = df.iloc[:, 1:].astype(float) / 4.41

                if selected_samples:
                    df = filter_samples(df, selected_samples)

                if not df.empty:
                    # Use the y-limits specific to the day
                    plot_data(df, day, day_y_limits[day])

def plot_data(df, day, y_limits):
    """
    Plot the data for a specific day with special handling for 'C', 'E1', and 'E2'.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data to plot.
        day (int): The day corresponding to the current data.
        y_limits (tuple): The y-axis limits for the plot.
    """
    plt.figure(figsize=(30, 10))  # Start a new figure

    # Set line width and marker size for better visibility
    line_width = 4
    marker_size = 8

    # Initialize list to hold x-tick positions and labels
    sample_labels = []
    x_positions = []

    # Separate the special cases
    c_rows = df[df['Sample'] == 'C']
    e1_rows = df[df['Sample'].str.contains('E1')]
    e2_rows = df[df['Sample'].str.contains('E2')]
    
    # Plot 'C', 'E1', and 'E2' rows with error bars
    # Similar to how you previously handled 'C', 'E1', and 'E2'
    # (code goes here)

    # Plot all other samples
    other_samples = df[~df['Sample'].str.contains('C|E1|E2')]
    for i, row in other_samples.iterrows():
        sample = row['Sample']
        mean_value = row[1:].mean()
        std_dev = row[1:].std()
        x_positions.append(len(x_positions))  # Position for each sample
        sample_labels.append(sample)
        plt.errorbar(x_positions[-1], mean_value, yerr=std_dev, fmt='o', capsize=10, lw=line_width, markersize=marker_size)

    # Finalize the plot
    plt.title(f"Ti Day {day} Data", fontsize=24)
    plt.ylabel('Cell Count per $mm^2$', fontsize=18)
    plt.ylim(y_limits[0] * 0.95, y_limits[1] * 1.05)  # Add 5% padding to y-limits
    plt.xticks(ticks=x_positions, labels=sample_labels, rotation=90, fontsize=18)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'C:/Users/User/OneDrive - Aarhus universitet/Master THesis/Figurer\DataMaster/Titanium/proliferation/Imprints(PCmedTI)/ {day} Day Combined.png')
    plt.show()

# Example usage
if __name__ == "__main__":
    source_folder = r'C:\Users\User\Desktop\Andreas script - Data folder\Andreas script - Data folder\Your cell data\Imprints(PCmedTI) resultater\Combined data'
    
    # Lists of valid values
    days = [1, 3, 5]
    
    # Define the samples you want to include
    selected_samples = []
    #selected_samples = ['1;2 (HEX)', '0.5;2 (HEX)', '1;0.5 (HEX)', '2;0.3 (HEX)', 'C']  # Replace with your actual sample names

    plot_excel_files(source_folder, days, selected_samples)
