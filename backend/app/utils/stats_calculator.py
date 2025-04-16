import logging


from capstone.backend.app.core import analysis_config as config

class StatsCalculator:
    def __init__(self):
        self.possession_frames_team = {0: 0, 1: 0}
        self.pass_counts_team = {0: 0, 1: 0}
        # Stores {'id': track_id, 'team': team_index} of the last player confirmed to have possession
        self.last_confirmed_possessor_info = {'id': None, 'team': -1}
        # Keep track of last logged values to only log changes
        self.last_logged_possession_percent = None
        self.last_logged_pass_count = None

    def _find_possessing_player(self, ball_center_orig: tuple, current_player_boxes: dict) -> int | None:
        """Finds the player closest to the ball within the threshold."""
        possessing_player_id = None
        min_dist_sq = config.POSSESSION_THRESHOLD_PIXELS**2

        if ball_center_orig is None:
            return None

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
            except Exception as e:
                logging.warning(f"Error calculating possession distance for player {p_id}: {e}")
                continue
        return possessing_player_id

    def update(self, frame_count: int, ball_center_orig: tuple | None, current_player_boxes: dict, current_frame_player_teams: dict):
        """Updates possession and pass counts based on current frame data."""
        possessing_player_id = self._find_possessing_player(ball_center_orig, current_player_boxes)

        current_possessor_team = -1
        if possessing_player_id is not None:
            current_possessor_team = current_frame_player_teams.get(possessing_player_id, -1)

            if current_possessor_team != -1:
                # Increment possession frames for the valid team
                self.possession_frames_team[current_possessor_team] += 1

                # --- Pass Detection Logic ---
                # Check if there was a previous possessor with a valid team
                if self.last_confirmed_possessor_info['id'] is not None and \
                   self.last_confirmed_possessor_info['team'] != -1:
                    # Check if the player ID changed BUT the team remained the SAME
                    if self.last_confirmed_possessor_info['id'] != possessing_player_id and \
                       self.last_confirmed_possessor_info['team'] == current_possessor_team:
                        # This indicates a pass within the same team
                        self.pass_counts_team[current_possessor_team] += 1
                        logging.info(f"Frame {frame_count}: Pass detected T{current_possessor_team + 1} "
                                     f"({self.last_confirmed_possessor_info['id']} -> {possessing_player_id})")

                # Update the last confirmed possessor regardless of pass detection
                self.last_confirmed_possessor_info['id'] = possessing_player_id
                self.last_confirmed_possessor_info['team'] = current_possessor_team

            else:
                pass

        else:
            # No player has possession this frame. Reset last confirmed possessor.
            self.last_confirmed_possessor_info = {'id': None, 'team': -1}


    def get_stats_update(self, frame_count: int) -> dict | None:
         """Calculates current stats and returns an update entry if changed since last log."""
         stats_changed = False
         current_stats_entry = {}

         # Calculate Possession %
         total_possession = sum(self.possession_frames_team.values())
         current_possession = {"team1": 0, "team2": 0}
         if total_possession > 0:
             perc_t1 = round((self.possession_frames_team[0] / total_possession) * 100)
             current_possession["team1"] = perc_t1
             current_possession["team2"] = 100 - perc_t1

         if current_possession != self.last_logged_possession_percent:
             current_stats_entry["POSSESSION"] = current_possession
             stats_changed = True

         # Get Pass Counts
         current_passes = {"team1": self.pass_counts_team[0], "team2": self.pass_counts_team[1]}
         if current_passes != self.last_logged_pass_count:
             # Only include teams with passes > 0 in the log entry
             pass_entry = {f"team{i+1}": count for i, count in enumerate([self.pass_counts_team[0], self.pass_counts_team[1]]) if count > 0}
             if pass_entry:
                  current_stats_entry["PASS"] = pass_entry
                  stats_changed = True

         # If stats changed, update last logged state and return the entry
         if stats_changed and current_stats_entry:
             self.last_logged_possession_percent = current_possession.copy()
             self.last_logged_pass_count = current_passes.copy()
             return {str(frame_count): current_stats_entry}
         else:
             return None

    def get_final_stats(self) -> dict:
         """Returns the final accumulated stats."""
         total_possession = sum(self.possession_frames_team.values())
         final_possession = {"team1": 0, "team2": 0}
         if total_possession > 0:
             perc_t1 = round((self.possession_frames_team[0] / total_possession) * 100)
             final_possession["team1"] = perc_t1
             final_possession["team2"] = 100 - perc_t1

         final_passes = {
             "team1": self.pass_counts_team[0],
             "team2": self.pass_counts_team[1]
         }
         return {"final_possession": final_possession, "final_passes": final_passes}