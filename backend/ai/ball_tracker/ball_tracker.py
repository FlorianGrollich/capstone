import logging
import os
import torch
import numpy as np
from collections import deque

from deep_sort_realtime.deepsort_tracker import DeepSort as BallDeepSortTracker

from capstone.backend.ai.ball_tracker.track_net import TrackNetV4

from capstone.backend.app.core import analysis_config as config
from capstone.backend.app.utils import video_utils

class BallTracker:
    def __init__(self, video_metadata: dict):
        self.model = self._load_model()
        self.tracker = BallDeepSortTracker(max_age=config.BALL_TRACKER_MAX_AGE,
                                           n_init=config.BALL_TRACKER_N_INIT,
                                           nms_max_overlap=config.BALL_TRACKER_NMS_OVERLAP)
        self.last_known_ball_center_model = None
        self.original_width = video_metadata['width']
        self.original_height = video_metadata['height']
        self.scale_width = self.original_width / config.TRACKNET_WIDTH
        self.scale_height = self.original_height / config.TRACKNET_HEIGHT

    def _load_model(self):
        if not os.path.exists(config.TRACKNET_MODEL_PATH):
            logging.error(f"TrackNet model not found at: {config.TRACKNET_MODEL_PATH}")
            raise FileNotFoundError(f"TrackNet model not found: {config.TRACKNET_MODEL_PATH}")
        try:
            model = TrackNetV4().to(config.DEVICE)
            # Use map_location for flexibility
            state_dict = torch.load(config.TRACKNET_MODEL_PATH, map_location=config.DEVICE, weights_only=True)
            model.load_state_dict(state_dict)
            model.eval()
            logging.info(f"TrackNet model loaded from {config.TRACKNET_MODEL_PATH} and set to eval mode.")
            return model
        except ImportError as imp_err:
             logging.error(f"Import error loading TrackNet model (check TrackNetV4 source/dependencies): {imp_err}")
             raise
        except Exception as e:
            logging.error(f"Error loading TrackNet model: {e}", exc_info=True)
            raise

    def _find_ball_peak(self, heatmap: torch.Tensor) -> tuple[int, int] | None:
        """Finds the peak in the heatmap, potentially using a search window."""
        ball_peak_found = False
        peak_y_model, peak_x_model = -1, -1

        # 1. Search window (if previous location known)
        if self.last_known_ball_center_model:
            prev_x_model, prev_y_model = self.last_known_ball_center_model
            y_min = int(max(0, prev_y_model - config.BALL_SEARCH_WINDOW_RADIUS))
            y_max = int(min(config.TRACKNET_HEIGHT, prev_y_model + config.BALL_SEARCH_WINDOW_RADIUS))
            x_min = int(max(0, prev_x_model - config.BALL_SEARCH_WINDOW_RADIUS))
            x_max = int(min(config.TRACKNET_WIDTH, prev_x_model + config.BALL_SEARCH_WINDOW_RADIUS))

            if y_min < y_max and x_min < x_max:
                heatmap_window = heatmap[y_min:y_max, x_min:x_max]
                if heatmap_window.numel() > 0:
                    max_conf_window, max_idx_window = torch.max(heatmap_window.reshape(-1), dim=0)
                    if max_conf_window.item() >= config.BALL_DETECTION_THRESHOLD:
                        window_y_rel, window_x_rel = divmod(max_idx_window.item(), heatmap_window.shape[1])
                        peak_y_model = y_min + window_y_rel
                        peak_x_model = x_min + window_x_rel
                        ball_peak_found = True

        # 2. Global search (if window search failed or no previous location)
        if not ball_peak_found:
            max_conf_global, max_idx_global = torch.max(heatmap.view(-1), dim=0)
            if max_conf_global.item() >= config.BALL_DETECTION_THRESHOLD:
                peak_y_model, peak_x_model = divmod(max_idx_global.item(), config.TRACKNET_WIDTH)
                ball_peak_found = True

        return (peak_y_model, peak_x_model) if ball_peak_found else None

    def track_ball(self, frame_buffer: deque, current_frame_for_deepsort: np.ndarray) -> tuple[tuple | None, bool]:
        """Processes frame buffer with TrackNet and updates DeepSORT."""
        ball_center_orig = None
        ball_tracked_this_frame = False
        detections_for_tracker = []

        try:
            tracknet_input = video_utils.prepare_tracknet_input(frame_buffer, config.TRACKNET_WIDTH, config.TRACKNET_HEIGHT)
            if tracknet_input is not None and self.model is not None:
                with torch.no_grad():
                    heatmap_output = self.model(tracknet_input)
                # Ensure the channel index is valid
                if config.TRACKNET_BALL_HEATMAP_CHANNEL < heatmap_output.shape[1]:
                     heatmap_current = torch.sigmoid(heatmap_output[0, config.TRACKNET_BALL_HEATMAP_CHANNEL].cpu())
                     peak_coords_model = self._find_ball_peak(heatmap_current)

                     if peak_coords_model:
                         peak_y_model, peak_x_model = peak_coords_model
                         # Convert model coords to original frame bbox for DeepSORT
                         center_x_orig = peak_x_model * self.scale_width
                         center_y_orig = peak_y_model * self.scale_height
                         width_orig = config.BALL_BOX_SIZE_MODEL * self.scale_width
                         height_orig = config.BALL_BOX_SIZE_MODEL * self.scale_height
                         left_orig = max(0.0, center_x_orig - (width_orig / 2))
                         top_orig = max(0.0, center_y_orig - (height_orig / 2))
                         # Ensure width/height don't extend beyond frame boundaries and are positive
                         w_final = max(1.0, width_orig if left_orig + width_orig <= self.original_width else self.original_width - left_orig)
                         h_final = max(1.0, height_orig if top_orig + height_orig <= self.original_height else self.original_height - top_orig)
                         bbox_xywh_original = [left_orig, top_orig, w_final, h_final]
                         # Confidence is high as it passed the heatmap threshold
                         detections_for_tracker.append((bbox_xywh_original, 0.9, 'ball'))
                else:
                    logging.warning(f"Invalid TRACKNET_BALL_HEATMAP_CHANNEL: {config.TRACKNET_BALL_HEATMAP_CHANNEL}")


            # Update DeepSORT tracker
            ball_tracks = self.tracker.update_tracks(detections_for_tracker, frame=current_frame_for_deepsort)
            confirmed_ball_tracks = [t for t in ball_tracks if t.is_confirmed()]

            best_ball_track = None
            if confirmed_ball_tracks:
                confirmed_ball_tracks.sort(key=lambda t: (t.time_since_update, -t.hits))
                best_ball_track = confirmed_ball_tracks[0]

            # Get center from the best confirmed track
            if best_ball_track and best_ball_track.time_since_update <= 1:
                 ltrb_ball = best_ball_track.to_tlbr()
                 cx_orig = (ltrb_ball[0] + ltrb_ball[2]) / 2
                 cy_orig = (ltrb_ball[1] + ltrb_ball[3]) / 2
                 ball_center_orig = (cx_orig, cy_orig)
                 self.last_known_ball_center_model = (cx_orig / self.scale_width, cy_orig / self.scale_height)
                 ball_tracked_this_frame = True
            else:
                 self.last_known_ball_center_model = None
                 ball_tracked_this_frame = False
                 if self.last_known_ball_center_model is not None:
                     logging.info(f"Ball track lost.")

        except Exception as e:
            logging.error(f"Error during ball tracking: {e}", exc_info=False)
            self.last_known_ball_center_model = None
            ball_center_orig = None
            ball_tracked_this_frame = False

        return ball_center_orig, ball_tracked_this_frame