import os
from PIL import Image, ImageDraw, ImageFont

# Define the grid size and empty fields
grid_size = 8
empty_fields = [1, 8, 16, 57, 64]

# Define the reference pixels per micrometer (adjust according to your reference images)
reference_ppm = 102.8  # This is the standard scale for 514 pixels = 5 µm

# Define the pixels per micrometer for specific fields
custom_ppm = {
    4: 137.2,  # Field 4 has 137.2 pixels per micrometer
    11: 171.4, # Field 11 has 171.4 pixels per micrometer
}

# Define the image size (cropped size)
crop_width = 1028  # Adjust to your needs
crop_height = 1028  # Adjust to your needs

# Load all images from the directory
image_dir = "C:/Users/User/Desktop/Master/Billeder til IMage/"  # Adjust this path to where your images are located
images = []
for i in range(1, grid_size*grid_size + 1):
    if i in empty_fields:
        images.append(None)
    else:
        # Determine the ppm based on the field number
        ppm = custom_ppm.get(i, reference_ppm)  # Use custom ppm if available, otherwise use reference ppm
        
        image_path = os.path.join(image_dir, f"Field{i}closeIM.tif")
        if not os.path.exists(image_path):
            print(f"File not found: {image_path}")
            images.append(None)
            continue
        
        img = Image.open(image_path)
        
        # Calculate the scaling factor
        scaling_factor = reference_ppm / ppm
        
        # Resize the image to match the reference scale
        new_size = (int(img.width * scaling_factor), int(img.height * scaling_factor))
        resized_img = img.resize(new_size, Image.LANCZOS)
        
        # Crop the resized image
        cropped_img = resized_img.crop((0, 0, crop_width, crop_height))  # Adjust cropping as needed
        
        images.append(cropped_img)

# Create a blank canvas for the 8x8 grid
grid_img = Image.new('RGB', (grid_size * crop_width, grid_size * crop_height), color='white')

# Load the font for numbering
try:
    font = ImageFont.truetype("arial.ttf", 120)  # Font size can be adjusted
except IOError:
    font = ImageFont.load_default()

# Paste the images into the grid and add numbers to each square
for i, img in enumerate(images):
    if img is not None:
        x = (i % grid_size) * crop_width
        y = (i // grid_size) * crop_height
        grid_img.paste(img, (x, y))
        
        # Draw the field number in the center of the square
        draw = ImageDraw.Draw(grid_img)
        number_text = str(i + 1)
        text_bbox = draw.textbbox((0, 0), number_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_position = (x + (crop_width - text_width) // 2, y + (crop_height - text_height) // 2)
        draw.text(text_position, number_text, fill="white", font=font)

# Parameters for the scale bar based on the new scale
scalebar_length_um = 10  # length of the scalebar in micrometers
scalebar_length_pixels = int(scalebar_length_um * reference_ppm)  # Convert to pixels

scalebar_height = 40   # Height of the scalebar in pixels (thicker)
scalebar_color = (255, 0, 0, 255)  # Color of the scalebar (red with full opacity)
scalebar_text = f"{scalebar_length_um} µm"  # Text to be displayed above the scalebar
text_color = 'red'  # Color of the text
text_size = 200  # Size of the text

# Load the font for the scalebar text
try:
    font = ImageFont.truetype("arial.ttf", text_size)
except IOError:
    font = ImageFont.load_default()

# Create an image for the combined scalebar and text with a transparent background
combined_scalebar = Image.new('RGBA', (scalebar_length_pixels, scalebar_height + text_size), (255, 255, 255, 0))

# Create an image for the text with a transparent background
text_img = Image.new('RGBA', (scalebar_length_pixels, text_size), (255, 255, 255, 0))  # Fully transparent background
text_draw = ImageDraw.Draw(text_img)
text_draw.text(((scalebar_length_pixels - text_draw.textlength(scalebar_text, font=font)) // 2, 0), 
               scalebar_text, fill=text_color, font=font)

# Draw the scalebar below the text
scalebar_img = Image.new('RGBA', (scalebar_length_pixels, scalebar_height), scalebar_color)
combined_scalebar.paste(scalebar_img, (0, text_size))
combined_scalebar.paste(text_img, (0, 0), text_img)  # Paste the text image with transparency

# Placement options
placement = 'bottom-right'  # Bottom-right placement

# Calculate position based on placement
if placement == 'bottom-right':
    scalebar_position = (grid_img.width - scalebar_length_pixels - 1028, grid_img.height - combined_scalebar.height - 100)

# Convert grid image to RGBA before pasting the scalebar
grid_img = grid_img.convert("RGBA")
grid_img.paste(combined_scalebar, scalebar_position, combined_scalebar)

# Convert the final image back to RGB
grid_img = grid_img.convert("RGB")

# Save the final grid image
output_path = "C:/Users/User/Desktop/Master/Billeder til IMage/grid_image_with_custom_scalebar.png"
grid_img.save(output_path, dpi=(300, 300))

print(f"Grid image saved to {output_path}")
