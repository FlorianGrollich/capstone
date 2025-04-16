import logging
import os
from ultralytics import YOLO
import numpy as np

# Assuming analysis_config is accessible
from capstone.backend.app.core import analysis_config as config
from capstone.backend.app.utils import video_utils

class PlayerTracker:
    def __init__(self):
        self.model = self._load_model()
        self.player_class_index = self._get_player_class_index()

    def _load_model(self):
        if not os.path.exists(config.YOLO_MODEL_PATH):
            logging.error(f"YOLO model not found at: {config.YOLO_MODEL_PATH}")
            raise FileNotFoundError(f"YOLO model not found: {config.YOLO_MODEL_PATH}")
        try:
            model = YOLO(config.YOLO_MODEL_PATH)
            logging.info(f"YOLO model loaded from {config.YOLO_MODEL_PATH}")
            return model
        except Exception as e:
            logging.error(f"Error loading YOLO model: {e}", exc_info=True)
            raise

    def _get_player_class_index(self):
        if not self.model or not hasattr(self.model, 'names'):
             logging.error("YOLO model not loaded or has no 'names' attribute.")
             return -1
        try:
            for index, name in self.model.names.items():
                if name == config.PLAYER_CLASS_NAME:
                    logging.info(f"Found player class '{config.PLAYER_CLASS_NAME}' at index {index}")
                    return index
            logging.error(f"Player class '{config.PLAYER_CLASS_NAME}' not found in model names: {self.model.names}")
            return -1
        except Exception as e:
             logging.error(f"Error accessing model names: {e}")
             return -1

    def track_players(self, frame: np.ndarray) -> tuple[dict, list, list, list]:
        """Tracks players in a frame and extracts features."""
        current_player_boxes = {} # {track_id: [x1, y1, x2, y2]}
        current_player_features_lab = []
        current_player_track_ids = []
        current_player_bboxes = []

        if not self.model or self.player_class_index == -1:
            return current_player_boxes, current_player_features_lab, current_player_track_ids, current_player_bboxes

        track_classes = [self.player_class_index]
        yolo_results = None
        try:
            yolo_results = self.model.track(frame, persist=True, verbose=False,
                                            conf=config.PLAYER_CONFIDENCE_THRESHOLD,
                                            iou=config.PLAYER_IOU_THRESHOLD,
                                            classes=track_classes)
        except Exception as track_err:
            logging.error(f"Error during YOLO track: {track_err}")
            return current_player_boxes, current_player_features_lab, current_player_track_ids, current_player_bboxes # Return empty

        if yolo_results and len(yolo_results) > 0 and yolo_results[0].boxes is not None and yolo_results[0].boxes.id is not None:
            try:
                boxes_xyxy = yolo_results[0].boxes.xyxy.cpu().numpy()
                track_ids = yolo_results[0].boxes.id.cpu().numpy().astype(int)

                for i, box in enumerate(boxes_xyxy):
                    track_id = -1
                    try:
                        track_id = track_ids[i]
                        x1, y1, x2, y2 = map(int, box)
                        if x1 >= x2 or y1 >= y2: continue # Skip invalid box

                        current_player_boxes[track_id] = [x1, y1, x2, y2]
                        player_crop = frame[y1:y2, x1:x2]
                        dom_lab = video_utils.get_dominant_color_lab_team(player_crop)

                        if dom_lab is not None:
                            current_player_features_lab.append(dom_lab)
                            current_player_track_ids.append(track_id)
                            current_player_bboxes.append((x1, y1, x2, y2))
                    except (IndexError, ValueError) as box_err:
                        logging.warning(f"Error processing player box {i} (Track ID {track_id if track_id !=-1 else 'N/A'}): {box_err}")
                        continue
            except AttributeError as attr_err:
                logging.warning(f"Attribute error processing YOLO tracking results: {attr_err}.")
            except Exception as proc_err:
                logging.warning(f"Error processing YOLO tracking results: {proc_err}")

        return current_player_boxes, current_player_features_lab, current_player_track_ids, current_player_bboxes