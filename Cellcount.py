# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 22:25:14 2024

@author: User
"""



import numpy as np
import cv2
import os
import pyvips
def extract_uv_image(vsi_path, output_dir):
    # Load the VSI file using pyvips
    image = pyvips.Image.new_from_file(vsi_path, access='sequential')

    # Convert the pyvips image to a numpy array
    image_data = np.ndarray(buffer=image.write_to_memory(),
                            dtype=np.uint8,
                            shape=[image.height, image.width, image.bands])

    # Assume the UV channel is one of the channels in the image (e.g., the last channel)
    # You might need to adjust this based on your specific data
    uv_channel_index = -1
    uv_image = image_data[:, :, uv_channel_index]

    # Normalize the UV image to the range 0-255 for saving as an 8-bit image
    uv_image_normalized = cv2.normalize(uv_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the UV image
    output_path = os.path.join(output_dir, 'uv_image.png')
    cv2.imwrite(output_path, uv_image_normalized)

    print(f'UV image extracted and saved to {output_path}')

# Example usage
vsi_path = r'C:\Users\User\Desktop\Master\29_5\Ti\Ti_1days.vsi'
output_dir = r'C:\Users\User\Desktop\Master\29_5\Ti'
extract_uv_image(vsi_path, output_dir)