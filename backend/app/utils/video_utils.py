import cv2
import torch
import numpy as np
from collections import deque
from skimage.color import rgb2lab
import logging
from capstone.backend.app.core import analysis_config as config



def get_dominant_color_lab_team(roi: np.ndarray) -> np.ndarray | None:
    """Finds dominant non-green color in LAB format."""
    if roi is None or roi.size == 0:
        return None
    dom_lab = None
    try:
        roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask_green = cv2.inRange(roi_hsv, config.LOWER_GREEN_HSV_TEAM, config.UPPER_GREEN_HSV_TEAM)
        mask_inv = cv2.bitwise_not(mask_green)
        non_bg_pixels_bgr = roi[mask_inv != 0]
        num_non_bg = len(non_bg_pixels_bgr)

        if num_non_bg < config.MIN_NON_BG_PIXELS_TEAM:
            return None

        pixels = non_bg_pixels_bgr.reshape(-1, 3).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, _, centers = cv2.kmeans(pixels, 1, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

        dominant_color_bgr = centers[0].astype(np.uint8)
        dominant_color_rgb = dominant_color_bgr[::-1] # BGR -> RGB
        dom_lab = rgb2lab(dominant_color_rgb.reshape(1, 1, 3) / 255.0)[0][0]
    except Exception as e:
        logging.debug(f"Internal error in get_dominant_color_lab_team: {e}")
    return dom_lab


def prepare_tracknet_input(frames: deque, width: int, height: int) -> torch.Tensor | None:
    """Prepares a deque of frames for TrackNet input."""
    if not frames or len(frames) != 3:
        return None
    tensor_list = []
    try:
        for frame in frames:
            resized_frame = cv2.resize(frame, (width, height))
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            frame_tensor = torch.from_numpy(rgb_frame).permute(2, 0, 1).float() / 255.0
            tensor_list.append(frame_tensor)

        input_tensor = torch.cat(tensor_list, dim=0)
        return input_tensor.unsqueeze(0).to(config.DEVICE)
    except Exception as e:
        logging.warning(f"Error preparing TrackNet input: {e}")
        return None

def get_video_metadata(video_path: str) -> dict | None:
    """Extracts metadata (dimensions, fps, frame count) from a video file."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error(f"Failed to open video file for metadata: {video_path}")
        return None
    try:
        metadata = {
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": int(cap.get(cv2.CAP_PROP_FPS)),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        }
        if metadata["fps"] <= 0:
            logging.warning(f"Video FPS reported as {metadata['fps']}, using fallback: 30")
            metadata["fps"] = 30
        if metadata["frame_count"] <= 0:
             logging.warning(f"Video frame count reported as {metadata['frame_count']}. Analysis might fail.")

    except Exception as e:
        logging.error(f"Error reading video metadata: {e}")
        metadata = None
    finally:
        cap.release()
    return metadata