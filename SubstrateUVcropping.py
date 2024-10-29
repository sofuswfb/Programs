
'''
This script aims to divide TIF files into manually drawn rectangles from TIF-
files and crop the same rectangle from the UV picture. 

Run the script. It will prompt you to select which image to use (Green Ex.tif, BF.tif, or Multi Fluo.tif).
After selecting the image, it will display the chosen image at a reasonable size for your screen.
Use the left mouse button to click and drag to define the top-left and bottom-right corners of multiple square overlays. You should see the rectangles as you drag.
Release the mouse button to finalize each selection. Repeat the process for additional rectangles.
Press any key to finish the drawing process and close the window.
The script will crop both the chosen image and the UV.tif image based on each drawn rectangle and save the cropped areas as new images in the same folder.

'''

import cv2
import numpy as np
from PIL import Image
import os

# Define paths to the possible input images
folder_path = 'C:/Users/User/Desktop/Master/29_5/Ti/_Ti_5days_/'
image_options = ['Green Ex.tif', 'BF.tif', 'Multi Fluo.tif']
image_paths = [os.path.join(folder_path, image) for image in image_options]

# Function to choose the image to use
def choose_image():
    print("Please choose an image to use:")
    for idx, image in enumerate(image_options):
        print(f"{idx + 1}. {image}")
    choice = int(input("Enter the number of your choice: "))
    if 1 <= choice <= len(image_options):
        return image_paths[choice - 1]
    else:
        print("Invalid choice. Exiting.")
        exit()

# Load the chosen image
chosen_image_path = choose_image()

try:
    chosen_image = Image.open(chosen_image_path)
    chosen_image_cv = np.array(chosen_image)
    print(f"{os.path.basename(chosen_image_path)} loaded successfully.")
except Exception as e:
    print(f"Failed to load the chosen image: {e}")
    exit()

# Load the UV image
uv_image_path = os.path.join(folder_path, 'UV.tif')
try:
    uv_image = Image.open(uv_image_path)
    uv_image_cv = np.array(uv_image)
    print("UV image loaded successfully.")
except Exception as e:
    print(f"Failed to load the UV image: {e}")
    exit()

# Resize the images for display while maintaining the aspect ratio
max_dimension = 800
height, width = chosen_image_cv.shape[:2]

if height > max_dimension or width > max_dimension:
    if height > width:
        scale = max_dimension / height
    else:
        scale = max_dimension / width
    chosen_image_cv = cv2.resize(chosen_image_cv, (int(width * scale), int(height * scale)))
    uv_image_cv = cv2.resize(uv_image_cv, (int(width * scale), int(height * scale)))

# Variables to store points and state
rectangles = []
drawing = False
current_rectangle = []

def draw_rectangle(event, x, y, flags, param):
    global rectangles, drawing, current_rectangle, chosen_image_cv, image_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        current_rectangle = [(x, y)]

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            image_copy = chosen_image_cv.copy()
            cv2.rectangle(image_copy, current_rectangle[0], (x, y), (255, 0, 0), 2)
            cv2.imshow('Chosen Image', image_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        current_rectangle.append((x, y))
        rectangles.append(current_rectangle)
        cv2.rectangle(chosen_image_cv, current_rectangle[0], current_rectangle[1], (255, 0, 0), 2)
        cv2.imshow('Chosen Image', chosen_image_cv)

# Display the image and set the mouse callback function
cv2.namedWindow('Chosen Image', cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback('Chosen Image', draw_rectangle)
cv2.imshow('Chosen Image', chosen_image_cv)
cv2.waitKey(0)
cv2.destroyAllWindows()

if not rectangles:
    print("No rectangles were drawn. Exiting.")
    exit()

# Function to save a cropped area
def save_cropped_area(image, left, upper, right, lower, base_name, index):
    square = image.crop((left, upper, right, lower))
    square_file_path = os.path.join(folder_path, f'{base_name}_cropped_{index}.tif')
    square.save(square_file_path)
    return square_file_path

# Load the original chosen image for accurate cropping
chosen_image = Image.open(chosen_image_path)

# Load the UV image again for accurate cropping
uv_image = Image.open(uv_image_path)

chosen_cropped_paths = []
uv_cropped_paths = []

# Process each rectangle
for index, rect in enumerate(rectangles):
    x1, y1 = rect[0]
    x2, y2 = rect[1]
    x1, y1 = int(x1 / scale), int(y1 / scale)
    x2, y2 = int(x2 / scale), int(y2 / scale)
    
    left = min(x1, x2)
    right = max(x1, x2)
    upper = min(y1, y2)
    lower = max(y1, y2)
    
    # Save the cropped areas for the chosen image
    chosen_cropped_path = save_cropped_area(chosen_image, left, upper, right, lower, os.path.basename(chosen_image_path).split('.')[0], index)
    chosen_cropped_paths.append(chosen_cropped_path)
    
    # Save the cropped areas for UV
    uv_cropped_path = save_cropped_area(uv_image, left, upper, right, lower, 'uv', index)
    uv_cropped_paths.append(uv_cropped_path)

# Output the paths of the saved cropped areas
print(f"{os.path.basename(chosen_image_path).split('.')[0]} cropped areas saved at:", chosen_cropped_paths)
print("UV cropped areas saved at:", uv_cropped_paths)
