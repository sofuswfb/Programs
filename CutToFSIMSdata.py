# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 15:48:23 2024

Dataanalysis of ToF-SIMS data. 

@author: User
"""
def delete_after_line(file_path, line_number):
    # Read the file content
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Keep only the lines up to the specified line number
    new_lines = lines[:line_number]

    # Write the new content back to the file
    with open(file_path, 'w') as file:
        file.writelines(new_lines)

    print(f"Deleted all lines after line {line_number} from the file.")

# Example usage
file_path = r'C:\Users\User\Desktop\Master\ToF-Sims\NoUVNeg\PC_NoUV_Spot3_neg_Bi3++_0 - Kopi.TXT'
delete_after_line(file_path, 158000)
