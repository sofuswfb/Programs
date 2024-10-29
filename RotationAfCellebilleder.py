# -*- coding: utf-8 -*-
'''
The script only works on images taken at 4x zoom on the microscope in Tandlaegeskolen
This script will use the multifluor and the UV images taken on this microscope

This needs to be done manually:
    Renaming files to make them compatible with Nicjolas' script (no spaces)
    Execution of Nicjolas' script to generate images from all 3 channels
    Execution of the rotation script to generate images where the substrate is at a right angle

'''

import numpy as np
import cv2

# Collection of corners for rotation
corners = []
# x and y values one is currently at on images
current_x, current_y = 0, 0

# Functions
def save_image_coordinates(event, x, y, flags, param):
    """
    Mouse callback function to get coordinates relative to the full image.
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(corners) < 2:
            # Calculate the coordinates relative to the full image
            zoom_factor = zoom_level / 100.0
            full_x = int(current_x + x / zoom_factor)
            full_y = int(current_y + y / zoom_factor)
            corners.append((full_x, full_y))
            print(f"Saved coordinates ({full_x}, {full_y})")


def rotate_image(corners, image, img_name):
    global path, img_path
    # The angle needed for rotaiton is calculated from two coordinates, the
    # calculation differs dependent on if the angle is positive or negative
    if len(corners) != 2:
        raise UserWarning('Choose to coordiantes on the image to continue')
    if corners[0][1] < corners[1][1]:
        rotation_degree = 180/np.pi * np.arccos((corners[1][0] - corners[0][0]) / np.sqrt((corners[1][0] - corners[0][0])**2 + (corners[1][1] - corners[0][1])**2))
    else:
        rotation_degree = -180/np.pi * np.arccos((corners[1][0] - corners[0][0]) / np.sqrt((corners[1][0] - corners[0][0])**2 + (corners[1][1] - corners[0][1])**2))

    # Get the image dimensions (height and width)
    (h, w) = image.shape[:2]
    
    # Calculate the center of the image
    center = (w / 2, h / 2)
    
    # Get the rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(center, rotation_degree, 1.0)
    
    # Calculate the new bounding dimensions of the image
    cos = np.abs(rotation_matrix[0, 0])
    sin = np.abs(rotation_matrix[0, 1])
    
    new_width = int((h * sin) + (w * cos))
    new_height = int((h * cos) + (w * sin))
    
    # Adjust the rotation matrix to take into account the translation
    rotation_matrix[0, 2] += (new_width / 2) - center[0]
    rotation_matrix[1, 2] += (new_height / 2) - center[1]
    
    # Perform the rotation
    rotated_image = cv2.warpAffine(image, rotation_matrix, (new_width, new_height))
    
    # Save the rotated image
    output_path = path + sample_folder + img_name
    cv2.imwrite(output_path, rotated_image)
    
    print()
    print(f"Rotated image saved as {output_path}")

def update_image(x, y, zoom, image, window_size):
    """
    Update the displayed image based on the trackbar positions and zoom level.
    """
    global current_x, current_y, zoom_level
    current_x, current_y = x, y
    zoom_level = zoom
    
    h, w = image.shape[:2]
    
    # Calculate the size of the displayed area based on zoom level
    zoom_factor = zoom / 100.0
    display_w = int(window_size / zoom_factor)
    display_h = int(window_size / zoom_factor)

    # Ensure the displayed area does not exceed the image dimensions
    x_end = min(x + display_w, w)
    y_end = min(y + display_h, h)
    cropped_image = image[y:y_end, x:x_end]

    # Resize the cropped image to fit the window size
    resized_image = cv2.resize(cropped_image, (window_size, window_size))
    cv2.imshow('Image Viewer', resized_image)

def on_trackbar(val, image, window_size):
    """
    Callback function for trackbar.
    """
    x = cv2.getTrackbarPos('X', 'Image Viewer')
    y = cv2.getTrackbarPos('Y', 'Image Viewer')
    zoom = cv2.getTrackbarPos('Zoom', 'Image Viewer')
    update_image(x, y, zoom, image, window_size)


# Execution
import sys

# Add the directory where the file is located to sys.path
sys.path.append(r'C:\Users\User\Desktop\Master\Titanium\proliferation\Imprints(PCmedTI)\dag_1_')

# Multifluo is treated. Image is loaded
# Name of Multi Fluo image
MF_img_name = 'BF.tif'

# The path is chosen by the user, only sample_folder is changed between samples
sample_folder = '\_Dag_5_sample_3_/'
path = r'C:\Users\User\Desktop\Master\Titanium\proliferation\Imprints(PCmedTI)\dag_5'
MFimage = cv2.imread(path + sample_folder + MF_img_name)

# Script stops if image is not loaded
if MFimage is None:
    print("Error loading image")
    raise UserWarning
else:
    print('Press two points which should be horizontal on the final image')

# Window size is chosen, it can result in the image looking distorted if not matching
# the screen size correctly, but it should not affect the resulting image
window_size = 500

# Image is shown, 'select_corners' is called so one can choose two corners that
# should be on the same x-axis. Choose corners far from each other for best results
cv2.imshow('Image Viewer', MFimage[:window_size, :window_size])
cv2.setMouseCallback('Image Viewer', save_image_coordinates)

# Trackbars are generated making it possible to change X, Y and Zoom
cv2.createTrackbar('X', 'Image Viewer', 0, max(0, MFimage.shape[1] - window_size), lambda val: on_trackbar(val, MFimage, window_size))
cv2.createTrackbar('Y', 'Image Viewer', 0, max(0, MFimage.shape[0] - window_size), lambda val: on_trackbar(val, MFimage, window_size))
cv2.createTrackbar('Zoom', 'Image Viewer', 100, 500, lambda val: on_trackbar(val, MFimage, window_size))  # Zoom range from 100% to 500%
cv2.waitKey(0)
cv2.destroyAllWindows()

# The function which can rotate images is called on the Multi Fluo image
rotate_image(corners, MFimage, 'Zbehandlet - Rotated BF image.tif')

print('Rotation of BF image was successful')

# UV is treated. Image is loaded
# Name of UV image
UV_img_name = 'UV.tif'
UVimage = cv2.imread(path + sample_folder + UV_img_name)

# Script is stopped of image is not properly loaded
if UVimage is None:
    print("Error loading image")
    exit(1)

# The function which can rotate images is called on the UV image
# The coordinates which are already chosen are reused, making sure that the
# multi fluo and UV image get the same rotation
rotate_image(corners, UVimage, 'Zbehandlet - Rotated UV image.tif')

print('Rotation of UV image was successful')
