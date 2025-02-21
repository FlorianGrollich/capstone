from ai.helpers.img_show import show
from helpers.detect_ball import detect_best_ball
from helpers.draw_ball import draw_ball
from helpers.merge_binary_img import merge_binary_images
from helpers.color_removal import color_removal
from helpers.hough_trasnform import hough_transform

from helpers.sobel import sobel
import cv2



def process_frame(frame):
    # Your existing processing pipeline
    i1 = sobel(frame)
    i2 = color_removal(frame)
    merged_images = merge_binary_images(i1, i2)

    merged_images_color = cv2.cvtColor(merged_images, cv2.COLOR_GRAY2BGR)
    hough = hough_transform(merged_images_color)

    hough = cv2.cvtColor(hough, cv2.COLOR_BGR2GRAY)
    best_ball = detect_best_ball(hough)

    # Draw ball if detected
    if best_ball is not None:
        frame = draw_ball(best_ball, frame.copy())
    return frame


def process_video(input_path, output_path):
    # Initialize video capture
    cap = cv2.VideoCapture(input_path)

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process frame
        processed_frame = process_frame(frame)

        # Write processed frame
        out.write(processed_frame)

    # Cleanup
    cap.release()
    out.release()
    cv2.destroyAllWindows()
img = cv2.imread("test_data/test4.png")
f = process_frame(img)
show(f)
