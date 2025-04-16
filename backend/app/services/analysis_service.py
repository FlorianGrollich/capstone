import logging
import time
import cv2
from collections import deque

from capstone.backend.app.core import analysis_config as config
from capstone.backend.app.utils import video_utils
from capstone.backend.app.utils.stats_calculator import StatsCalculator

from capstone.backend.ai.player_tracker.player_tracker import PlayerTracker
from capstone.backend.ai.ball_tracker.ball_tracker import BallTracker
from capstone.backend.ai.team_identifier import TeamIdentifier

logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)

async def run_video_analysis(video_path: str) -> dict:
    """
    Orchestrates the video analysis process using refactored components.
    """
    logging.info(f"Starting analysis for video: {video_path}")
    analysis_start_time = time.time()
    stats_log = {"stats": {}}
    final_summary = {}


    video_metadata = video_utils.get_video_metadata(video_path)
    if not video_metadata:
        return {"error": "Failed to read video metadata."}
    if video_metadata["frame_count"] <= 0:
         logging.warning(f"Video has {video_metadata['frame_count']} frames. Cannot analyze.")
         return {"error": "Video has zero or negative frames."}

    logging.info(f"Video Info: {video_metadata['width']}x{video_metadata['height']} "
                 f"@ {video_metadata['fps']}fps, {video_metadata['frame_count']} frames.")


    try:
        player_tracker = PlayerTracker()
        team_identifier = TeamIdentifier()

        ball_tracker = BallTracker(video_metadata)
        stats_calculator = StatsCalculator()
    except (FileNotFoundError, ImportError, Exception) as e:
        logging.error(f"Failed to initialize analysis components: {e}", exc_info=True)
        return {"error": f"Initialization failed: {e}"}


    try:
        team_identifier.initialize_teams(video_path, player_tracker)
    except Exception as e:
        logging.error(f"Error during team initialization phase: {e}", exc_info=True)

        logging.warning("Proceeding without team identification.")


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

        frame_buffer.append(original_frame.copy())
        frame_count += 1

        if frame_count % 200 == 0 or frame_count == 1:
            logging.info(f"Analyzer processing frame {frame_count}/{video_metadata['frame_count']}")


        if len(frame_buffer) == 3:
            current_frame_original = frame_buffer[1]

            try:

                player_boxes, player_features, player_ids, _ = player_tracker.track_players(current_frame_original)


                current_teams = team_identifier.assign_teams_for_frame(player_features, player_ids)


                ball_center, ball_tracked = ball_tracker.track_ball(frame_buffer, current_frame_original)


                stats_calculator.update(frame_count, ball_center, player_boxes, current_teams)

                stat_update = stats_calculator.get_stats_update(frame_count)
                if stat_update:
                    stats_log["stats"].update(stat_update)

            except Exception as loop_err:
                 logging.error(f"Error during processing frame {frame_count}: {loop_err}", exc_info=False)

                 continue


    cap.release()
    logging.info("Finished processing loop.")


    final_summary = stats_calculator.get_final_stats()
    stats_log["summary"] = final_summary

    analysis_duration = time.time() - analysis_start_time
    logging.info(f"Analysis took {analysis_duration:.2f} seconds.")

    if not stats_log["stats"] and not final_summary:
        logging.warning("Analysis completed but no statistics were logged or calculated.")
        stats_log["message"] = "No significant statistics generated."


    return stats_log