import cv2
import numpy as np


def sobel(image):
    i = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(i, cv2.CV_64F, 1, 0, ksize=1)
    sobely = cv2.Sobel(i, cv2.CV_64F, 0, 1, ksize=1)

    gradient_magnitude = cv2.magnitude(sobelx, sobely)
    # Normalize to the range [0, 255] and convert to uint8
    gradient_magnitude = cv2.normalize(gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX)
    gradient_magnitude = np.uint8(gradient_magnitude)

    _, binary_image = cv2.threshold(gradient_magnitude, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return binary_image

i = cv2.imread('test2.jpg', flags=3)
print(sobel(i).shape)
