# video_analyzer.py

import cv2
import torch
import numpy as np
from collections import deque
import os
import time
import logging
from ultralytics import YOLO
from sklearn.cluster import KMeans
from skimage.color import rgb2lab

from deep_sort_realtime.deepsort_tracker import DeepSort as BallDeepSortTracker

from capstone.backend.ai.ball_tracker.track_net import TrackNetV4

# --- Configuration ---
# Model Paths (Ensure these are correct relative to script execution)
YOLO_MODEL_PATH = "../../ai/player_tracker/best.pt"
TRACKNET_MODEL_PATH = "../../ai/ball_tracker/tracknetv4.pth"

# Processing Parameters
TRACKNET_WIDTH = 1024
TRACKNET_HEIGHT = 576
PLAYER_CONFIDENCE_THRESHOLD = 0.4
PLAYER_IOU_THRESHOLD = 0.5
PLAYER_CLASS_NAME = 'player' # Verify this matches your YOLO model output
INITIALIZATION_FRAMES = 50
MIN_NON_BG_PIXELS_TEAM = 50
LOWER_GREEN_HSV_TEAM = np.array([30, 40, 40])
UPPER_GREEN_HSV_TEAM = np.array([90, 255, 255])
BALL_DETECTION_THRESHOLD = 0.3
BALL_BOX_SIZE_MODEL = 15
BALL_SEARCH_WINDOW_RADIUS = 50
BALL_TRACKER_MAX_AGE = 10
BALL_TRACKER_N_INIT = 3
TRACKNET_BALL_HEATMAP_CHANNEL = 1 # Critical: Verify this channel index
POSSESSION_THRESHOLD_PIXELS = 150

# Visualization Colors (Not used if drawing is removed, but kept for context)
TEAM_VIZ_COLORS = {0: (255, 100, 0), 1: (0, 100, 255), -1: (200, 200, 200)}
# --- End Configuration ---

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.basicConfig(level=logging.INFO, format='ANALYZER - %(levelname)s: %(message)s')

# --- Helper Functions ---
def get_dominant_color_lab_team(roi: np.ndarray) -> np.ndarray | None:
    """Finds dominant non-green color in LAB format."""
    if roi is None or roi.size == 0:
        return None
    dom_lab = None # Initialize
    try:
        roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask_green = cv2.inRange(roi_hsv, LOWER_GREEN_HSV_TEAM, UPPER_GREEN_HSV_TEAM)
        mask_inv = cv2.bitwise_not(mask_green)
        non_bg_pixels_bgr = roi[mask_inv != 0]
        num_non_bg = len(non_bg_pixels_bgr)

        if num_non_bg < MIN_NON_BG_PIXELS_TEAM:
            return None

        pixels = non_bg_pixels_bgr.reshape(-1, 3).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        # Use PP centers for better initialization
        _, _, centers = cv2.kmeans(pixels, 1, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

        dominant_color_bgr = centers[0].astype(np.uint8)
        dominant_color_rgb = dominant_color_bgr[::-1] # BGR -> RGB
        # Reshape for rgb2lab: requires (M,N,3) or (1,1,3)
        dom_lab = rgb2lab(dominant_color_rgb.reshape(1, 1, 3) / 255.0)[0][0]
    except Exception as e:
        # Log internal errors for debugging if needed
        logging.debug(f"Internal error in get_dominant_color_lab_team: {e}")
        # Returns the initial None value

    return dom_lab

def prepare_tracknet_input(frames: deque, width: int, height: int) -> torch.Tensor | None:
    """Prepares a deque of frames for TrackNet input."""
    if not frames or len(frames) != 3: # Ensure buffer has correct size
        return None
    tensor_list = []
    try:
        for frame in frames:
            resized_frame = cv2.resize(frame, (width, height))
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            # HWC to CHW, normalize
            frame_tensor = torch.from_numpy(rgb_frame).permute(2, 0, 1).float() / 255.0
            tensor_list.append(frame_tensor)
        # Concatenate along channel dimension (or time, depending on model input spec)
        # Assuming TrackNet expects input shape like (Batch, Channels*Time, H, W)
        input_tensor = torch.cat(tensor_list, dim=0)
        # Add batch dimension
        return input_tensor.unsqueeze(0).to(device)
    except Exception as e:
        logging.warning(f"Error preparing TrackNet input: {e}")
        return None
# --- End Helper Functions ---

# --- Main Analysis Function ---
async def run_video_analysis(video_path: str) -> dict:
    """
    Analyzes the video at the given path and returns statistics.
    """
    logging.info(f"Starting analysis for video: {video_path}")
    analysis_start_time = time.time()
    stats_log = {"stats": {}} # Initialize empty log

    # --- Load Models ---
    yolo_model = None
    tracknet_model = None
    try:
        # Resolve paths relative to this script file
        script_dir = os.path.dirname(__file__)
        yolo_model_load_path = os.path.abspath(os.path.join(script_dir, YOLO_MODEL_PATH))
        tracknet_model_load_path = os.path.abspath(os.path.join(script_dir, TRACKNET_MODEL_PATH))

        if not os.path.exists(yolo_model_load_path):
             raise FileNotFoundError(f"YOLO model not found at resolved path: {yolo_model_load_path}")
        yolo_model = YOLO(yolo_model_load_path)
        logging.info(f"YOLO model loaded from {yolo_model_load_path}")

        # Verify player class name AFTER loading model
        if PLAYER_CLASS_NAME not in yolo_model.names.values():
             available_classes = list(yolo_model.names.values())
             logging.error(f"Player class '{PLAYER_CLASS_NAME}' not found in YOLO model names: {yolo_model.names}. Available: {available_classes}")
             return stats_log # Return empty if config mismatch

        if not os.path.exists(tracknet_model_load_path):
             raise FileNotFoundError(f"TrackNet model not found at resolved path: {tracknet_model_load_path}")
        tracknet_model = TrackNetV4().to(device)
        # Use map_location for flexibility if model was trained on different device
        state_dict = torch.load(tracknet_model_load_path, map_location=device, weights_only=True)
        tracknet_model.load_state_dict(state_dict)
        tracknet_model.eval() # Set model to evaluation mode
        logging.info(f"TrackNet model loaded from {tracknet_model_load_path} and set to eval mode.")

    except ImportError as imp_err:
        logging.error(f"Import error loading models (check paths/dependencies): {imp_err}")
        return stats_log
    except FileNotFoundError as fnf_err:
        logging.error(f"Model file not found: {fnf_err}")
        return stats_log
    except Exception as e:
        logging.error(f"Error loading models for analysis: {e}", exc_info=True)
        return stats_log

    # --- Get Video Info ---
    cap_info = cv2.VideoCapture(video_path)
    if not cap_info.isOpened():
        logging.error(f"Failed to open video file for analysis: {video_path}")
        return stats_log

    original_width = int(cap_info.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap_info.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap_info.get(cv2.CAP_PROP_FPS))
    if fps <= 0: # Check for 0 or negative FPS
        fps = 30 # Fallback
        logging.warning("Video FPS reported as <= 0, using fallback: 30")
    total_frames = int(cap_info.get(cv2.CAP_PROP_FRAME_COUNT))
    cap_info.release()

    if total_frames <= 0: # Check for 0 or negative frames
        logging.warning(f"Video has {total_frames} frames. Cannot analyze: {video_path}")
        return stats_log

    logging.info(f"Video Info: {original_width}x{original_height} @ {fps}fps, {total_frames} frames.")
    scale_width = original_width / TRACKNET_WIDTH
    scale_height = original_height / TRACKNET_HEIGHT

    # --- Phase 1: Team Color Clustering ---
    logging.info("Starting team color clustering phase...")
    reference_team_colors = [None, None]
    teams_initialized = False
    cap_cluster = cv2.VideoCapture(video_path)
    cluster_frame_count = 0
    player_colors_lab_samples = []

    if cap_cluster.isOpened():
        while cap_cluster.isOpened() and cluster_frame_count < INITIALIZATION_FRAMES:
            ret, frame = cap_cluster.read()
            if not ret:
                break # Exit loop if frame cannot be read
            cluster_frame_count += 1
            dom_lab = None # Initialize dom_lab for this frame iteration

            try: # Wrap predict call
                 results = yolo_model.predict(frame, conf=PLAYER_CONFIDENCE_THRESHOLD, verbose=False)

                 # Correct iteration for predict results
                 if results and results[0].boxes is not None:
                     boxes_obj = results[0].boxes # Get the Boxes object
                     num_boxes = len(boxes_obj)
                     if num_boxes > 0:
                         # Get tensors for all boxes once
                         xyxy_tensor = boxes_obj.xyxy.cpu().numpy()
                         conf_tensor = boxes_obj.conf.cpu().numpy()
                         cls_tensor = boxes_obj.cls.cpu().numpy()

                         # Iterate through boxes using an index
                         for i in range(num_boxes):
                             # dom_lab initialized above loop for the frame
                             try:
                                 x1, y1, x2, y2 = xyxy_tensor[i]
                                 conf = conf_tensor[i]
                                 cls_id = cls_tensor[i]
                                 cls_id_int = int(cls_id)

                                 if cls_id_int not in yolo_model.names:
                                     continue # Skip unknown class IDs

                                 if yolo_model.names[cls_id_int] == PLAYER_CLASS_NAME:
                                     # Convert coords and check validity
                                     x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                                     if x1 >= x2 or y1 >= y2:
                                         continue # Skip invalid box dimensions

                                     # Extract color
                                     player_crop = frame[y1:y2, x1:x2]
                                     dom_lab = get_dominant_color_lab_team(player_crop) # Assign here
                                     if dom_lab is not None:
                                         player_colors_lab_samples.append(dom_lab)

                             except (ValueError, IndexError, KeyError) as box_proc_err:
                                  logging.warning(f"Error processing single box data (clustering) idx {i}: {box_proc_err}")
                                  continue # Skip this box
            except Exception as pred_err:
                 logging.warning(f"Error during predict call in clustering F{cluster_frame_count}: {pred_err}", exc_info=False)
                 continue # Skip this frame on predict error
        cap_cluster.release()

    # --- K-Means Clustering after sample gathering ---
    logging.info(f" Clustering: Gathered {len(player_colors_lab_samples)} samples.")
    if len(player_colors_lab_samples) >= 10: # Need a reasonable number
        clustering_data = np.array(player_colors_lab_samples)
        try:
            logging.info(" Running K-Means...")
            kmeans = KMeans(n_clusters=2, n_init=10, random_state=0)
            kmeans.fit(clustering_data)
            initial_centers = kmeans.cluster_centers_
            color_diff = np.linalg.norm(initial_centers[0] - initial_centers[1])

            if color_diff < 20: # LAB distance threshold
                 logging.warning(f"Team centroids similar (LAB Dist: {color_diff:.1f}). Separation might be poor.")

            # Assign Team 1 (index 0) to the darker color based on Lightness L*
            if initial_centers[0][0] <= initial_centers[1][0]:
                reference_team_colors[0] = initial_centers[0] # Team 1 Ref
                reference_team_colors[1] = initial_centers[1] # Team 2 Ref
            else:
                reference_team_colors[0] = initial_centers[1] # Team 1 Ref
                reference_team_colors[1] = initial_centers[0] # Team 2 Ref
            teams_initialized = True
            logging.info("*** Teams initialized successfully ***")
            logging.info(f"  Reference Team 1 (Darker) LAB: {reference_team_colors[0]}")
            logging.info(f"  Reference Team 2 (Lighter) LAB: {reference_team_colors[1]}")

        except Exception as e:
            logging.error(f"Error during K-Means clustering: {e}", exc_info=True)
            teams_initialized = False # Ensure flag is false if clustering failed
    else:
        logging.warning("Not enough color samples gathered for clustering. Team assignment will be disabled.")
        teams_initialized = False # Explicitly set if not enough samples

    # --- Initialize Trackers and Stats Variables ---
    logging.info("Initializing trackers and main loop variables...")
    ball_tracker = BallDeepSortTracker(max_age=BALL_TRACKER_MAX_AGE, n_init=BALL_TRACKER_N_INIT, nms_max_overlap=1.0)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error(f"Failed to reopen video for main processing: {video_path}")
        return stats_log # Cannot proceed

    frame_buffer = deque(maxlen=3)
    last_known_ball_center_model = None
    possession_frames_team = {0: 0, 1: 0}
    pass_counts_team = {0: 0, 1: 0}
    last_confirmed_passer_info = {'id': None, 'team': -1} # Store last player ID and team with valid possession
    last_logged_possession_percent = None
    last_logged_pass_count = None

    # --- Main Processing Loop ---
    logging.info("Starting main processing loop...")
    with torch.no_grad(): # Disable gradient calculations for inference
        frame_count = 0
        while cap.isOpened():
            ret, original_frame = cap.read()
            if not ret:
                logging.info("End of video or cannot read frame.")
                break # Exit loop

            frame_buffer.append(original_frame)
            frame_count += 1

            # Log progress periodically
            if frame_count % 200 == 0 or frame_count == 1:
                logging.info(f" Analyzer processing frame {frame_count}/{total_frames}")

            # Need 3 frames in buffer for TrackNet
            if len(frame_buffer) == 3:
                # Use the middle frame of the buffer for current analysis
                current_frame_original = frame_buffer[1].copy()

                # --- 1. Player Tracking ---
                player_class_index = -1
                try:
                    for index, name in yolo_model.names.items():
                        if name == PLAYER_CLASS_NAME:
                            player_class_index = index
                            break
                except Exception as e:
                    logging.warning(f"Could not access model names correctly: {e}")

                track_classes = [player_class_index] if player_class_index != -1 else None
                if track_classes is None:
                    # Warning already logged if player_class_index is -1
                    pass # logging.warning(f"Frame {frame_count}: Tracking ALL classes.")

                yolo_results = None # Initialize
                try:
                    yolo_results = yolo_model.track(current_frame_original, persist=True, verbose=False,
                                                    conf=PLAYER_CONFIDENCE_THRESHOLD, iou=PLAYER_IOU_THRESHOLD,
                                                    classes=track_classes)
                except Exception as track_err:
                    logging.error(f"Error during YOLO track on frame {frame_count}: {track_err}")
                    continue # Skip rest of processing for this frame

                # --- Extract Player Features ---
                current_player_boxes = {} # {track_id: [x1, y1, x2, y2]}
                current_player_features_lab = [] # Features for *this frame*
                current_player_track_ids_in_frame = [] # Track IDs corresponding to features
                current_player_bboxes_in_frame = [] # BBoxes corresponding to features

                if yolo_results and len(yolo_results) > 0 and yolo_results[0].boxes is not None and yolo_results[0].boxes.id is not None:
                    try: # Wrap processing of tracking results
                        player_boxes_xyxy = yolo_results[0].boxes.xyxy.cpu().numpy()
                        player_track_ids = yolo_results[0].boxes.id.cpu().numpy().astype(int)

                        for i, box in enumerate(player_boxes_xyxy):
                            track_id = -1 # Initialize track_id
                            try:
                                track_id = player_track_ids[i]
                                x1, y1, x2, y2 = map(int, box)
                                current_player_boxes[track_id] = [x1, y1, x2, y2] # Store box for possession check

                                # Extract features for team assignment
                                if x1 >= x2 or y1 >= y2:
                                    continue # Skip invalid boxes
                                player_crop = current_frame_original[y1:y2, x1:x2]
                                dom_lab = get_dominant_color_lab_team(player_crop)
                                if dom_lab is not None:
                                    current_player_features_lab.append(dom_lab)
                                    current_player_track_ids_in_frame.append(track_id)
                                    current_player_bboxes_in_frame.append((x1, y1, x2, y2))
                            except (IndexError, ValueError) as box_err:
                                logging.warning(f"Error processing player box {i} (Track ID {track_id if track_id !=-1 else 'N/A'}) F{frame_count}: {box_err}")
                                continue # Skip this box

                    except AttributeError as attr_err:
                        logging.warning(f"Attribute error processing YOLO tracking results F{frame_count}: {attr_err}. Tracking might be incompatible.")
                    except Exception as proc_err:
                        logging.warning(f"Error processing YOLO tracking results F{frame_count}: {proc_err}")

                # --- 2. Team Assignment ---
                current_frame_player_teams = {} # {track_id: team_index}
                num_players_for_clustering = len(current_player_features_lab)

                if teams_initialized and num_players_for_clustering >= 2:
                    features = np.array(current_player_features_lab)
                    try:
                        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
                        kmeans.fit(features)
                        current_labels = kmeans.labels_ # Labels from this frame's KMeans (0 or 1)
                        current_centers = kmeans.cluster_centers_

                        # Match current centers to reference centers
                        dist0_ref0 = np.linalg.norm(current_centers[0] - reference_team_colors[0])
                        dist0_ref1 = np.linalg.norm(current_centers[0] - reference_team_colors[1])
                        dist1_ref0 = np.linalg.norm(current_centers[1] - reference_team_colors[0])
                        dist1_ref1 = np.linalg.norm(current_centers[1] - reference_team_colors[1])
                        cost_direct = dist0_ref0 + dist1_ref1
                        cost_flipped = dist0_ref1 + dist1_ref0

                        # Determine mapping based on cost
                        if cost_direct <= cost_flipped:
                            map_kmeans0_to_team_idx = 0
                            map_kmeans1_to_team_idx = 1
                        else:
                            map_kmeans0_to_team_idx = 1
                            map_kmeans1_to_team_idx = 0

                        # Apply mapping to players clustered in *this frame*
                        for i, k_label in enumerate(current_labels):
                            track_id = current_player_track_ids_in_frame[i]
                            if k_label == 0:
                                current_frame_player_teams[track_id] = map_kmeans0_to_team_idx
                            else: # k_label == 1
                                current_frame_player_teams[track_id] = map_kmeans1_to_team_idx

                    except Exception as e:
                        logging.warning(f"KMeans/Assignment error frame {frame_count}: {e}.")
                        # No team assignments if clustering fails this frame

                # --- 3. Ball Tracking ---
                ball_detections_for_tracker = []
                best_ball_track = None
                ball_center_orig = None
                ball_tracked_this_frame = False

                try:
                    tracknet_input_tensor = prepare_tracknet_input(frame_buffer, TRACKNET_WIDTH, TRACKNET_HEIGHT)
                    if tracknet_input_tensor is not None:
                        ball_heatmap_output = tracknet_model(tracknet_input_tensor)
                        ball_heatmap_current = torch.sigmoid(ball_heatmap_output[0, TRACKNET_BALL_HEATMAP_CHANNEL].cpu())
                        ball_peak_found = False
                        ball_peak_y_model, ball_peak_x_model = -1, -1

                        # Search window logic
                        if last_known_ball_center_model:
                            prev_x_model, prev_y_model = last_known_ball_center_model
                            y_min = int(max(0, prev_y_model - BALL_SEARCH_WINDOW_RADIUS))
                            y_max = int(min(TRACKNET_HEIGHT, prev_y_model + BALL_SEARCH_WINDOW_RADIUS))
                            x_min = int(max(0, prev_x_model - BALL_SEARCH_WINDOW_RADIUS))
                            x_max = int(min(TRACKNET_WIDTH, prev_x_model + BALL_SEARCH_WINDOW_RADIUS))
                            if y_min < y_max and x_min < x_max:
                                heatmap_window = ball_heatmap_current[y_min:y_max, x_min:x_max]
                                if heatmap_window.numel() > 0:
                                    max_conf_window, max_idx_window = torch.max(heatmap_window.reshape(-1), dim=0)
                                    if max_conf_window.item() >= BALL_DETECTION_THRESHOLD:
                                        window_y_rel, window_x_rel = divmod(max_idx_window.item(), heatmap_window.shape[1])
                                        ball_peak_y_model = y_min + window_y_rel
                                        ball_peak_x_model = x_min + window_x_rel
                                        ball_peak_found = True
                        # Global search if needed
                        if not ball_peak_found:
                            max_conf_global, max_idx_global = torch.max(ball_heatmap_current.view(-1), dim=0)
                            if max_conf_global.item() >= BALL_DETECTION_THRESHOLD:
                                ball_peak_y_model, ball_peak_x_model = divmod(max_idx_global.item(), TRACKNET_WIDTH)
                                ball_peak_found = True

                        # Create detection for DeepSORT
                        if ball_peak_found:
                            center_x_orig = ball_peak_x_model * scale_width
                            center_y_orig = ball_peak_y_model * scale_height
                            width_orig = BALL_BOX_SIZE_MODEL * scale_width
                            height_orig = BALL_BOX_SIZE_MODEL * scale_height
                            left_orig = max(0.0, center_x_orig - (width_orig / 2))
                            top_orig = max(0.0, center_y_orig - (height_orig / 2))
                            w_final = max(1.0, width_orig if left_orig + width_orig <= original_width else original_width - left_orig)
                            h_final = max(1.0, height_orig if top_orig + height_orig <= original_height else original_height - top_orig)
                            bbox_xywh_original = [left_orig, top_orig, w_final, h_final]
                            ball_detections_for_tracker.append((bbox_xywh_original, 0.9, 'ball'))

                    # Update DeepSORT
                    ball_tracks = ball_tracker.update_tracks(ball_detections_for_tracker, frame=current_frame_original)
                    confirmed_ball_tracks = [t for t in ball_tracks if t.is_confirmed()]
                    if confirmed_ball_tracks:
                        confirmed_ball_tracks.sort(key=lambda t: (t.time_since_update, -t.hits))
                        best_ball_track = confirmed_ball_tracks[0]

                    # Store ball center and Log
                    if best_ball_track and best_ball_track.time_since_update <= 1:
                         ltrb_ball = best_ball_track.to_tlbr()
                         cx_orig = (ltrb_ball[0] + ltrb_ball[2]) / 2
                         cy_orig = (ltrb_ball[1] + ltrb_ball[3]) / 2
                         ball_center_orig = (cx_orig, cy_orig)
                         last_known_ball_center_model = (cx_orig / scale_width, cy_orig / scale_height)
                         ball_tracked_this_frame = True
                    else:
                         if last_known_ball_center_model is not None:
                             logging.info(f"Frame {frame_count}: Ball track lost.")
                         last_known_ball_center_model = None
                         ball_center_orig = None
                         ball_tracked_this_frame = False
                except Exception as e:
                    logging.error(f"Error during ball tracking frame {frame_count}: {e}", exc_info=False)
                    last_known_ball_center_model = None
                    ball_center_orig = None
                    ball_tracked_this_frame = False

                # --- 4. Possession Calculation ---
                possessing_player_id = None
                min_dist_sq = POSSESSION_THRESHOLD_PIXELS**2

                if ball_center_orig is not None:
                    ball_cx, ball_cy = ball_center_orig
                    for p_id, p_box in current_player_boxes.items():
                        try:
                             p_x1, p_y1, p_x2, p_y2 = p_box
                             player_cx = (p_x1 + p_x2) / 2
                             player_cy = (p_y1 + p_y2) / 2
                             dist_sq = (ball_cx - player_cx)**2 + (ball_cy - player_cy)**2
                             if dist_sq < min_dist_sq:
                                 min_dist_sq = dist_sq
                                 possessing_player_id = p_id
                        except Exception as poss_calc_err:
                             logging.warning(f"Error calculating possession for player {p_id} F{frame_count}: {poss_calc_err}")
                             continue

                # --- 5. Update Statistics (Refined pass logic) ---
                current_possession_holder_team = -1
                current_possessor_valid_team = False

                if possessing_player_id is not None:
                    current_possession_holder_team = current_frame_player_teams.get(possessing_player_id, -1)
                    if current_possession_holder_team != -1:
                        possession_frames_team[current_possession_holder_team] += 1
                        current_possessor_valid_team = True

                        # Pass detection
                        if last_confirmed_passer_info['id'] is not None and \
                           last_confirmed_passer_info['id'] != possessing_player_id and \
                           last_confirmed_passer_info['team'] == current_possession_holder_team:
                            pass_counts_team[current_possession_holder_team] += 1
                            logging.info(f"Frame {frame_count}: Pass detected T{current_possession_holder_team + 1} ({last_confirmed_passer_info['id']} -> {possessing_player_id})")

                        # Update last confirmed passer info *only* if current holder is valid
                        last_confirmed_passer_info['id'] = possessing_player_id
                        last_confirmed_passer_info['team'] = current_possession_holder_team

                # --- 6. Calculate Stats & Check for JSON Log Update ---
                stats_changed = False
                current_stats_entry = {}

                # Calculate Possession %
                total_possession_frames = possession_frames_team[0] + possession_frames_team[1]
                current_possession_percent = {"team1": 0, "team2": 0}
                if total_possession_frames > 0:
                    perc_t1 = round((possession_frames_team[0] / total_possession_frames) * 100)
                    current_possession_percent["team1"] = perc_t1
                    current_possession_percent["team2"] = 100 - perc_t1

                # Check if possession changed from last log
                if current_possession_percent != last_logged_possession_percent:
                     current_stats_entry["POSSESSION"] = current_possession_percent
                     stats_changed = True

                # Get Pass Counts
                current_pass_count = {"team1": pass_counts_team[0], "team2": pass_counts_team[1]}
                # Check if passes changed from last log
                if current_pass_count != last_logged_pass_count:
                    pass_entry = {f"team{i+1}": count for i, count in enumerate([pass_counts_team[0], pass_counts_team[1]]) if count > 0}
                    if pass_entry:
                        current_stats_entry["PASS"] = pass_entry
                        stats_changed = True

                # If any stat changed, add entry to log and update last logged state
                if stats_changed and current_stats_entry:
                    stats_log["stats"][str(frame_count)] = current_stats_entry
                    last_logged_possession_percent = current_possession_percent.copy()
                    last_logged_pass_count = current_pass_count.copy()

                # --- 7. Drawing (Can be commented out for API focus) ---
                # ... (Drawing code if needed) ...

    # --- End Main Loop ---
    cap.release()
    logging.info("Finished processing loop.")
    analysis_duration = time.time() - analysis_start_time
    logging.info(f"Analysis took {analysis_duration:.2f} seconds.")

    # Make sure stats log is not empty before returning
    if not stats_log["stats"]:
        logging.warning("Analysis completed but no statistics were logged.")

    return stats_log