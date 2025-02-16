import numpy as np
from PIL import Image
import cv2


# Load the image
img = cv2.imread('dataset/data/extracted_frames/image-239.jpg', cv2.IMREAD_GRAYSCALE)
# Check if the image is loaded correctly
if img is None:
    raise ValueError("Image not found or cannot be loaded.")

# Convert to binary image
_, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)


# Initialize skeleton and temporary images
skel = np.zeros(img.shape, np.uint8)
temp = np.zeros(img.shape, np.uint8)
eroded = np.zeros(img.shape, np.uint8)

# Structuring element
element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

done = False
while not done:
    # Erode the image
    cv2.erode(img, element, eroded)

    # Dilate the eroded image
    cv2.dilate(eroded, element, temp)  # temp = open(img)

    # Subtract the dilated image from the original
    cv2.subtract(img, temp, temp)

    # Update the skeleton
    cv2.bitwise_or(skel, temp, skel)

    # Copy the eroded image to the original image
    img[:] = eroded[:]

    # Ensure that 'img' is a single-channel image before counting non-zero pixels
    if len(img.shape) == 2 and img.dtype == np.uint8:
        done = cv2.countNonZero(img) == 0
    else:
        raise ValueError("The image should be a single-channel grayscale image.")


cv2.namedWindow('Skeleton', cv2.WINDOW_NORMAL)
height, width = skel.shape[:2]
cv2.resizeWindow('Skeleton', width, height)
cv2.imshow('Skeleton', skel)
cv2.waitKey(0)
cv2.destroyAllWindows()