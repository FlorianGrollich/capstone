from helpers.detect_ball import detect_best_ball
from helpers.draw_ball import draw_ball
from helpers.merge_binary_img import merge_binary_images
from helpers.color_removal import color_removal
from helpers.hough_trasnform import hough_transform
from helpers.img_show import show
from helpers.sobel import sobel
import cv2

i = cv2.imread('test_data/test2.jpg', flags=3)
i1 = sobel(i)
i2 = color_removal(i)

merged_images = merge_binary_images(i1, i2)
merged_images_color = cv2.cvtColor(merged_images, cv2.COLOR_GRAY2BGR)
hough = hough_transform(merged_images_color)

hough = cv2.cvtColor(hough, cv2.COLOR_BGR2GRAY)
best_ball = detect_best_ball(hough)

output_img = i.copy()

if best_ball is not None:
    output_img = draw_ball(best_ball, output_img)

# Save or display the result
show(output_img)
