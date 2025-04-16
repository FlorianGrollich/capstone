import pytest
from unittest.mock import patch, MagicMock
import logging

from capstone.backend.app.utils.stats_calculator import StatsCalculator
from capstone.backend.app.core import analysis_config as config


class TestStatsCalculator:
    @pytest.fixture
    def calculator(self):
        return StatsCalculator()

    def test_init(self, calculator):
        assert calculator.possession_frames_team == {0: 0, 1: 0}
        assert calculator.pass_counts_team == {0: 0, 1: 0}
        assert calculator.last_confirmed_possessor_info == {'id': None, 'team': -1}
        assert calculator.last_logged_possession_percent is None
        assert calculator.last_logged_pass_count is None

    def test_find_possessing_player_no_ball(self, calculator):
        player_boxes = {1: [10, 10, 30, 30], 2: [50, 50, 70, 70]}
        result = calculator._find_possessing_player(None, player_boxes)
        assert result is None

    @patch('capstone.backend.app.core.analysis_config.POSSESSION_THRESHOLD_PIXELS', 20)
    def test_find_possessing_player_with_player_nearby(self, calculator):
        ball_center = (20, 20)  # Ball is at (20, 20)
        player_boxes = {
            1: [10, 10, 30, 30],  # Player 1 center is at (20, 20) - within threshold
            2: [50, 50, 70, 70]  # Player 2 center is at (60, 60) - outside threshold
        }
        result = calculator._find_possessing_player(ball_center, player_boxes)
        assert result == 1

    @patch('capstone.backend.app.core.analysis_config.POSSESSION_THRESHOLD_PIXELS', 10)
    def test_find_possessing_player_no_player_nearby(self, calculator):
        ball_center = (40, 40)  # Ball is at (40, 40)
        player_boxes = {
            1: [10, 10, 30, 30],  # Player 1 center is at (20, 20) - outside threshold
            2: [50, 50, 70, 70]  # Player 2 center is at (60, 60) - outside threshold
        }
        result = calculator._find_possessing_player(ball_center, player_boxes)
        assert result is None

    @patch('logging.warning')
    def test_find_possessing_player_error_handling(self, mock_warning, calculator):
        ball_center = (20, 20)
        player_boxes = {
            1: [10, 10, 30, 30],  # Valid box
            2: [50, 50]  # Invalid box (should cause exception)
        }
        result = calculator._find_possessing_player(ball_center, player_boxes)
        assert result == 1  # Should still find player 1
        mock_warning.assert_called_once()  # Should log warning for player 2

    def test_update_no_possessing_player(self, calculator):
        calculator.update(
            frame_count=1,
            ball_center_orig=None,
            current_player_boxes={1: [10, 10, 30, 30], 2: [50, 50, 70, 70]},
            current_frame_player_teams={1: 0, 2: 1}
        )

        # No possession should be counted
        assert calculator.possession_frames_team == {0: 0, 1: 0}

        # Last confirmed possessor should be reset
        assert calculator.last_confirmed_possessor_info == {'id': None, 'team': -1}

    def test_update_with_possession(self, calculator):
        # Player 1 (team 0) has possession
        calculator.update(
            frame_count=1,
            ball_center_orig=(20, 20),
            current_player_boxes={1: [10, 10, 30, 30], 2: [50, 50, 70, 70]},
            current_frame_player_teams={1: 0, 2: 1}
        )

        # Team 0 should have 1 possession frame
        assert calculator.possession_frames_team == {0: 1, 1: 0}

        # Last confirmed possessor should be updated
        assert calculator.last_confirmed_possessor_info == {'id': 1, 'team': 0}

    def test_update_pass_detection(self, calculator):
        # Set up initial possession
        calculator.last_confirmed_possessor_info = {'id': 1, 'team': 0}

        # Pass from player 1 to player 3 (same team)
        calculator.update(
            frame_count=1,
            ball_center_orig=(60, 60),
            current_player_boxes={1: [10, 10, 30, 30], 3: [50, 50, 70, 70]},
            current_frame_player_teams={1: 0, 3: 0}
        )

        # Team 0 should have 1 pass
        assert calculator.pass_counts_team == {0: 1, 1: 0}

        # Last confirmed possessor should be updated
        assert calculator.last_confirmed_possessor_info == {'id': 3, 'team': 0}

    def test_get_stats_update_no_change(self, calculator):
        # Set initial state
        calculator.possession_frames_team = {0: 50, 1: 50}
        calculator.last_logged_possession_percent = {"team1": 50, "team2": 50}
        calculator.pass_counts_team = {0: 5, 1: 3}
        calculator.last_logged_pass_count = {"team1": 5, "team2": 3}

        update = calculator.get_stats_update(frame_count=100)

        # No change from last logged values, should return None
        assert update is None

    def test_get_stats_update_with_changes(self, calculator):
        # Set initial state
        calculator.possession_frames_team = {0: 60, 1: 40}
        calculator.last_logged_possession_percent = {"team1": 50, "team2": 50}
        calculator.pass_counts_team = {0: 5, 1: 3}
        calculator.last_logged_pass_count = {"team1": 4, "team2": 3}

        update = calculator.get_stats_update(frame_count=100)

        # Should return an update with the new values
        assert update == {"100": {
            "POSSESSION": {"team1": 60, "team2": 40},
            "PASS": {"team1": 5, "team2": 3}
        }}

    def test_get_final_stats(self, calculator):
        # Set some stats
        calculator.possession_frames_team = {0: 70, 1: 30}
        calculator.pass_counts_team = {0: 8, 1: 5}

        final_stats = calculator.get_final_stats()

        assert final_stats == {
            "final_possession": {"team1": 70, "team2": 30},
            "final_passes": {"team1": 8, "team2": 5}
        }