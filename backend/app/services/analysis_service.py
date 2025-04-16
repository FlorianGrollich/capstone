import logging
import time
import cv2
from collections import deque

# Configuration and Utilities
from capstone.backend.app.core import analysis_config as config
from capstone.backend.app.utils import video_utils
from capstone.backend.app.utils.stats_calculator import StatsCalculator

# AI Components
from capstone.backend.ai.player_tracker.player_tracker import PlayerTracker
from capstone.backend.ai.ball_tracker.ball_tracker import BallTracker
from capstone.backend.ai.team_identifier import TeamIdentifier

# Configure logging for the service
logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)

async def run_video_analysis(video_path: str) -> dict:
    """
    Orchestrates the video analysis process using refactored components.
    """
    logging.info(f"Starting analysis for video: {video_path}")
    analysis_start_time = time.time()
    stats_log = {"stats": {}} # Log changes over time
    final_summary = {} # Overall summary

    # --- 1. Get Video Info ---
    video_metadata = video_utils.get_video_metadata(video_path)
    if not video_metadata:
        return {"error": "Failed to read video metadata."}
    if video_metadata["frame_count"] <= 0:
         logging.warning(f"Video has {video_metadata['frame_count']} frames. Cannot analyze.")
         return {"error": "Video has zero or negative frames."}

    logging.info(f"Video Info: {video_metadata['width']}x{video_metadata['height']} "
                 f"@ {video_metadata['fps']}fps, {video_metadata['frame_count']} frames.")

    # --- 2. Initialize Components ---
    try:
        player_tracker = PlayerTracker() # Loads YOLO model internally
        team_identifier = TeamIdentifier()
        # Ball tracker needs video dimensions for scaling
        ball_tracker = BallTracker(video_metadata) # Loads TrackNet internally
        stats_calculator = StatsCalculator()
    except (FileNotFoundError, ImportError, Exception) as e:
        logging.error(f"Failed to initialize analysis components: {e}", exc_info=True)
        return {"error": f"Initialization failed: {e}"}

    # --- 3. Initialize Team Reference Colors ---
    # This requires reading initial frames and using the player tracker
    try:
        team_identifier.initialize_teams(video_path, player_tracker)
    except Exception as e:
        logging.error(f"Error during team initialization phase: {e}", exc_info=True)
        # Continue analysis? Or return error? Let's continue without team data.
        logging.warning("Proceeding without team identification.")
        # team_identifier.teams_initialized will be False

    # --- 4. Main Processing Loop ---
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error(f"Failed to reopen video for main processing: {video_path}")
        return {"error": "Failed to open video for processing."}

    frame_buffer = deque(maxlen=3)
    frame_count = 0
    logging.info("Starting main processing loop...")

    while cap.isOpened():
        ret, original_frame = cap.read()
        if not ret:
            logging.info("End of video or cannot read frame.")
            break

        frame_buffer.append(original_frame.copy()) # Add copy to buffer
        frame_count += 1

        if frame_count % 200 == 0 or frame_count == 1:
            logging.info(f"Analyzer processing frame {frame_count}/{video_metadata['frame_count']}")

        # Need 3 frames for TrackNet
        if len(frame_buffer) == 3:
            # Use the middle frame for player/ball tracking alignment
            current_frame_original = frame_buffer[1]

            try:
                # --- Player Tracking & Feature Extraction ---
                player_boxes, player_features, player_ids, _ = player_tracker.track_players(current_frame_original)

                # --- Team Assignment (Frame-level) ---
                current_teams = team_identifier.assign_teams_for_frame(player_features, player_ids)

                # --- Ball Tracking ---
                # Pass the full buffer, but the current frame for DeepSORT context
                ball_center, ball_tracked = ball_tracker.track_ball(frame_buffer, current_frame_original)

                # --- Statistics Update ---
                stats_calculator.update(frame_count, ball_center, player_boxes, current_teams)

                # --- Log Stat Changes ---
                stat_update = stats_calculator.get_stats_update(frame_count)
                if stat_update:
                    stats_log["stats"].update(stat_update)

            except Exception as loop_err:
                 logging.error(f"Error during processing frame {frame_count}: {loop_err}", exc_info=False)
                 # Decide whether to continue or break on error
                 continue # Skip this frame

    # --- 5. Cleanup and Final Stats ---
    cap.release()
    logging.info("Finished processing loop.")

    # Add final summary stats
    final_summary = stats_calculator.get_final_stats()
    stats_log["summary"] = final_summary # Add summary to the output

    analysis_duration = time.time() - analysis_start_time
    logging.info(f"Analysis took {analysis_duration:.2f} seconds.")

    if not stats_log["stats"] and not final_summary:
        logging.warning("Analysis completed but no statistics were logged or calculated.")
        # Return summary even if empty, or return a specific message
        stats_log["message"] = "No significant statistics generated."


    return stats_log