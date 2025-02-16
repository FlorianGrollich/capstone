from color_removal import color_removal
from hough_trasnform import hough_transform
from img_show import show
from sobel import sobel
import cv2
import numpy as np

i = cv2.imread('test2.jpg', flags=3)
i1 = sobel(i)
i2 = color_removal(i)


def merge_binary_images(img1, img2):
    # Ensure both images are binary (0 or 255)
    _, img1 = cv2.threshold(img1, 127, 255, cv2.THRESH_BINARY)
    _, img2 = cv2.threshold(img2, 127, 255, cv2.THRESH_BINARY)

    # Merge using logical OR: White pixels from either image are kept
    merged = cv2.bitwise_or(img1, img2)
    return merged
merged_images = merge_binary_images(i1,i2)
merged_images_color = cv2.cvtColor(merged_images, cv2.COLOR_GRAY2BGR)
hough = hough_transform(merged_images_color)



hough = cv2.cvtColor(hough, cv2.COLOR_BGR2GRAY)
contours, _ = cv2.findContours(hough, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Initialize variables to store the best ball candidate
best_ball = None
max_circularity = 0

# Thresholds (adjust based on your dataset)
min_area = 20  # Minimum area of the ball in pixels
max_area = 500  # Maximum area of the ball in pixels
min_circularity = 0.7  # Circularity threshold (1 = perfect circle)

for contour in contours:
    # Calculate area and perimeter
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)

    # Skip if area is too small/large or perimeter is 0
    if area < min_area or area > max_area or perimeter == 0:
        continue

    # Calculate circularity: (4*pi*A)/(P^2)
    circularity = (4 * np.pi * area) / (perimeter ** 2)

    # Calculate aspect ratio of bounding box
    _, _, w, h = cv2.boundingRect(contour)
    aspect_ratio = float(w) / h if w > h else float(h) / w

    # Check thresholds for circularity and aspect ratio
    if circularity > min_circularity and aspect_ratio < 1.5:
        if circularity > max_circularity:
            max_circularity = circularity
            best_ball = contour


output_img = i.copy()

if best_ball is not None:

    (x, y), radius = cv2.minEnclosingCircle(best_ball)
    center = (int(x), int(y))
    radius = int(radius)
    cv2.circle(output_img, center, radius, (0, 255, 0), 2)
    cv2.putText(output_img, 'Ball', (center[0], center[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Save or display the result
show(output_img)
