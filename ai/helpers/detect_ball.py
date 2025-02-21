import cv2
import numpy as np


def detect_best_ball(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize variables to store the best ball candidate
    best_ball = None
    max_circularity = 0

    # Thresholds (adjust based on your dataset)
    min_area = 20  # Minimum area of the ball in pixels
    max_area = 500  # Maximum area of the ball in pixels
    min_circularity = 0.1  # Circularity threshold (1 = perfect circle)

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
    return best_ball
