import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from capstone.backend.app.core.config import Settings
from capstone.backend.app.schemas.user import UserModel
from capstone.backend.app.schemas.token import TokenData
from capstone.backend.app.utils.authentication import (
    verify_password,
    get_password_hash,
    create_jwt,
    decode_jwt
)


class TestPasswordFunctions:
    def test_password_hash_and_verify(self):
        password = "securePassword123!"
        hashed = get_password_hash(password)


        assert hashed != password


        assert verify_password(password, hashed) is True

 
        assert verify_password("wrongPassword", hashed) is False

    @patch('capstone.backend.app.core.config.Settings.pwd_ctx')  # Fix: patch class variable
    def test_verify_password(self, mock_pwd_ctx):
        mock_pwd_ctx.verify.return_value = True
        assert verify_password("password", "hashed_password") is True
        mock_pwd_ctx.verify.assert_called_once_with("password", "hashed_password")

        mock_pwd_ctx.verify.return_value = False
        assert verify_password("password", "hashed_password") is False

    @patch('capstone.backend.app.core.config.Settings.pwd_ctx')  # Fix: patch class variable
    def test_get_password_hash(self, mock_pwd_ctx):
        mock_pwd_ctx.hash.return_value = "hashed_result"
        result = get_password_hash("password")
        assert result == "hashed_result"
        mock_pwd_ctx.hash.assert_called_once_with("password")