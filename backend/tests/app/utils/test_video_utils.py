import pytest
import numpy as np
import cv2
import torch
from collections import deque
import os
import tempfile
from unittest.mock import patch, MagicMock

from capstone.backend.app.utils.video_utils import (
    get_dominant_color_lab_team,
    prepare_tracknet_input,
    get_video_metadata
)
from capstone.backend.app.core import analysis_config as config


class TestGetDominantColorLabTeam:
    def test_valid_roi_with_dominant_color(self):
        # Create an image with red dominant color and some green
        roi = np.zeros((100, 100, 3), dtype=np.uint8)
        roi[30:70, 30:70] = [0, 0, 255]  # Red rectangle
        roi[0:20, 0:20] = [0, 255, 0]  # Green corner (should be ignored)

        result = get_dominant_color_lab_team(roi)

        assert result is not None
        # Check if result has L*a*b* components
        assert len(result) == 3
        # Red in LAB should have high positive a* value
        assert result[1] > 50

    def test_mostly_green_roi(self):
        # Create an image that's mostly green (should return None)
        roi = np.zeros((100, 100, 3), dtype=np.uint8)
        roi[:, :] = [0, 255, 0]  # All green
        roi[40:45, 40:45] = [0, 0, 255]  # Tiny red section (too small)

        result = get_dominant_color_lab_team(roi)

        assert result is None

    def test_empty_roi(self):
        result = get_dominant_color_lab_team(np.array([]))
        assert result is None

    def test_none_roi(self):
        result = get_dominant_color_lab_team(None)
        assert result is None

    @patch('cv2.cvtColor')
    def test_exception_handling(self, mock_cvt_color):
        mock_cvt_color.side_effect = Exception("Test exception")
        roi = np.zeros((100, 100, 3), dtype=np.uint8)

        result = get_dominant_color_lab_team(roi)

        assert result is None


class TestPrepareTracknetInput:
    def test_valid_frames(self):
        frames = deque([
            np.zeros((480, 640, 3), dtype=np.uint8),
            np.ones((480, 640, 3), dtype=np.uint8) * 127,
            np.ones((480, 640, 3), dtype=np.uint8) * 255
        ])

        result = prepare_tracknet_input(frames, 224, 224)

        assert result is not None
        assert isinstance(result, torch.Tensor)
        assert result.shape == (1, 9, 224, 224)  # (batch, channels*frames, height, width)

        # Check scaling to [0,1] range
        assert torch.min(result) >= 0
        assert torch.max(result) <= 1

    def test_insufficient_frames(self):
        frames = deque([
            np.zeros((480, 640, 3), dtype=np.uint8),
            np.ones((480, 640, 3), dtype=np.uint8) * 127
        ])

        result = prepare_tracknet_input(frames, 224, 224)

        assert result is None

    def test_empty_frames(self):
        frames = deque()

        result = prepare_tracknet_input(frames, 224, 224)

        assert result is None

    def test_none_frames(self):
        result = prepare_tracknet_input(None, 224, 224)

        assert result is None

    @patch('cv2.resize')
    def test_exception_handling(self, mock_resize):
        mock_resize.side_effect = Exception("Test exception")
        frames = deque([
            np.zeros((480, 640, 3), dtype=np.uint8),
            np.ones((480, 640, 3), dtype=np.uint8) * 127,
            np.ones((480, 640, 3), dtype=np.uint8) * 255
        ])

        result = prepare_tracknet_input(frames, 224, 224)

        assert result is None


class TestGetVideoMetadata:
    @pytest.fixture
    def mock_video_file(self):
        # Create a temporary file to use as a mock video
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        temp_file.close()
        yield temp_file.name
        os.unlink(temp_file.name)

    @patch('cv2.VideoCapture')
    def test_valid_video(self, mock_cap, mock_video_file):
        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = True
        mock_instance.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080,
            cv2.CAP_PROP_FPS: 30,
            cv2.CAP_PROP_FRAME_COUNT: 300
        }.get(prop, 0)
        mock_cap.return_value = mock_instance

        result = get_video_metadata(mock_video_file)

        assert result is not None
        assert result["width"] == 1920
        assert result["height"] == 1080
        assert result["fps"] == 30
        assert result["frame_count"] == 300

    @patch('cv2.VideoCapture')
    def test_video_open_failure(self, mock_cap, mock_video_file):
        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = False
        mock_cap.return_value = mock_instance

        result = get_video_metadata(mock_video_file)

        assert result is None

    @patch('cv2.VideoCapture')
    def test_invalid_fps(self, mock_cap, mock_video_file):
        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = True
        mock_instance.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080,
            cv2.CAP_PROP_FPS: 0,  # Invalid FPS
            cv2.CAP_PROP_FRAME_COUNT: 300
        }.get(prop, 0)
        mock_cap.return_value = mock_instance

        result = get_video_metadata(mock_video_file)

        assert result is not None
        assert result["fps"] == 30  # Should default to 30

    @patch('cv2.VideoCapture')
    def test_exception_handling(self, mock_cap, mock_video_file):
        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = True
        mock_instance.get.side_effect = Exception("Test exception")
        mock_cap.return_value = mock_instance

        result = get_video_metadata(mock_video_file)

        assert result is None