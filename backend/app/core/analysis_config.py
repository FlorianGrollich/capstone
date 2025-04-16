import numpy as np
import torch
import os

# --- Device ---
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- Model Paths ---
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
YOLO_MODEL_PATH = os.path.join(BACKEND_DIR, "ai/player_tracker/player_model_weights.pt")
TRACKNET_MODEL_PATH = os.path.join(BACKEND_DIR, "ai/ball_tracker/ball_model_weights.pth")

# --- Processing Parameters ---
TRACKNET_WIDTH = 1024
TRACKNET_HEIGHT = 576
PLAYER_CONFIDENCE_THRESHOLD = 0.4
PLAYER_IOU_THRESHOLD = 0.5
PLAYER_CLASS_NAME = 'player'

# --- Team Identification Parameters ---
INITIALIZATION_FRAMES = 50
MIN_NON_BG_PIXELS_TEAM = 50
LOWER_GREEN_HSV_TEAM = np.array([30, 40, 40])
UPPER_GREEN_HSV_TEAM = np.array([90, 255, 255])
TEAM_CLUSTERING_MIN_SAMPLES = 10
TEAM_SIMILARITY_THRESHOLD_LAB = 20

# --- Ball Tracking Parameters ---
BALL_DETECTION_THRESHOLD = 0.3
BALL_BOX_SIZE_MODEL = 15
BALL_SEARCH_WINDOW_RADIUS = 50
BALL_TRACKER_MAX_AGE = 10
BALL_TRACKER_N_INIT = 3
BALL_TRACKER_NMS_OVERLAP = 1.0
TRACKNET_BALL_HEATMAP_CHANNEL = 1

# --- Statistics Parameters ---
POSSESSION_THRESHOLD_PIXELS = 150

# --- Logging ---
LOG_FORMAT = 'ANALYZER - %(module)s - %(levelname)s: %(message)s'

# --- Visualization (Optional) ---
# TEAM_VIZ_COLORS = {0: (255, 100, 0), 1: (0, 100, 255), -1: (200, 200, 200)}