import cv2

def merge_binary_images(img1, img2):
    # Ensure both images are binary (0 or 255)
    _, img1 = cv2.threshold(img1, 127, 255, cv2.THRESH_BINARY)
    _, img2 = cv2.threshold(img2, 127, 255, cv2.THRESH_BINARY)

    # Merge using logical OR: White pixels from either image are kept
    merged = cv2.bitwise_or(img1, img2)
    return merged