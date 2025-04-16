import logging
import numpy as np
import cv2
from sklearn.cluster import KMeans


from capstone.backend.app.core import analysis_config as config
from capstone.backend.app.utils import video_utils

from capstone.backend.ai.player_tracker.player_tracker import PlayerTracker


class TeamIdentifier:
    def __init__(self):
        self.reference_team_colors_lab = [None, None]
        self.teams_initialized = False
        self.kmeans_ref = KMeans(n_clusters=2, n_init=10, random_state=0)
        self.kmeans_frame = KMeans(n_clusters=2, n_init=10, random_state=42)

    def initialize_teams(self, video_path: str, player_tracker: PlayerTracker):
        """Performs initial clustering to find reference team colors."""
        logging.info("Starting team color clustering phase...")
        cap_cluster = cv2.VideoCapture(video_path)
        if not cap_cluster.isOpened():
            logging.error(f"Failed to open video for team clustering: {video_path}")
            return

        cluster_frame_count = 0
        player_colors_lab_samples = []

        while cap_cluster.isOpened() and cluster_frame_count < config.INITIALIZATION_FRAMES:
            ret, frame = cap_cluster.read()
            if not ret: break
            cluster_frame_count += 1

            _, features, _, _ = player_tracker.track_players(frame)
            if features:
                 player_colors_lab_samples.extend(features)

        cap_cluster.release()
        logging.info(f"Clustering: Gathered {len(player_colors_lab_samples)} samples.")

        if len(player_colors_lab_samples) >= config.TEAM_CLUSTERING_MIN_SAMPLES:
            clustering_data = np.array(player_colors_lab_samples)
            try:
                logging.info("Running K-Means for reference colors...")
                self.kmeans_ref.fit(clustering_data)
                initial_centers = self.kmeans_ref.cluster_centers_
                color_diff = np.linalg.norm(initial_centers[0] - initial_centers[1])

                if color_diff < config.TEAM_SIMILARITY_THRESHOLD_LAB:
                    logging.warning(f"Team centroids similar (LAB Dist: {color_diff:.1f}). Separation might be poor.")

                # Assign Team 1 (index 0) to the darker color based on Lightness L*
                if initial_centers[0][0] <= initial_centers[1][0]:
                    self.reference_team_colors_lab[0] = initial_centers[0]
                    self.reference_team_colors_lab[1] = initial_centers[1]
                else:
                    self.reference_team_colors_lab[0] = initial_centers[1]
                    self.reference_team_colors_lab[1] = initial_centers[0]

                self.teams_initialized = True
                logging.info("*** Teams initialized successfully ***")
                logging.info(f"  Reference Team 1 (Darker) LAB: {self.reference_team_colors_lab[0]}")
                logging.info(f"  Reference Team 2 (Lighter) LAB: {self.reference_team_colors_lab[1]}")

            except Exception as e:
                logging.error(f"Error during K-Means clustering for init: {e}", exc_info=True)
                self.teams_initialized = False
        else:
            logging.warning("Not enough color samples for clustering. Team assignment disabled.")
            self.teams_initialized = False


    def assign_teams_for_frame(self, player_features_lab: list, player_track_ids: list) -> dict:
        """Assigns team indices (0 or 1) to players based on features for the current frame."""
        current_frame_player_teams = {}
        if not self.teams_initialized or len(player_features_lab) < 2:
            return current_frame_player_teams

        features = np.array(player_features_lab)
        try:
            self.kmeans_frame.fit(features)
            current_labels = self.kmeans_frame.labels_
            current_centers = self.kmeans_frame.cluster_centers_

            # Match current centers to reference centers
            dist0_ref0 = np.linalg.norm(current_centers[0] - self.reference_team_colors_lab[0])
            dist0_ref1 = np.linalg.norm(current_centers[0] - self.reference_team_colors_lab[1])
            dist1_ref0 = np.linalg.norm(current_centers[1] - self.reference_team_colors_lab[0])
            dist1_ref1 = np.linalg.norm(current_centers[1] - self.reference_team_colors_lab[1])

            # Determine mapping: map current cluster index (0 or 1) to reference team index (0 or 1)
            if (dist0_ref0 + dist1_ref1) <= (dist0_ref1 + dist1_ref0):
                map_kmeans_to_team = {0: 0, 1: 1}
            else:
                map_kmeans_to_team = {0: 1, 1: 0}

            # Apply mapping
            for i, k_label in enumerate(current_labels):
                track_id = player_track_ids[i]
                current_frame_player_teams[track_id] = map_kmeans_to_team[k_label]

        except Exception as e:
            logging.warning(f"KMeans/Assignment error during frame processing: {e}.")
            # Return empty dict if clustering/assignment fails for the frame

        return current_frame_player_teams