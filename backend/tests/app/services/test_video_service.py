import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from capstone.backend.app.schemas.user import UserModel, AuthenticationDTO
from capstone.backend.app.services.user_service import UserService


@pytest.fixture
def user_collection():
    return AsyncMock()


@pytest.fixture
def user_service(user_collection):
    return UserService(user_collection)


@pytest.fixture
def sample_user_dict():
    return {
        "email": "test@example.com",
        "password": "hashed_password123",
        "_id": "user_id_123"
    }


@pytest.fixture
def sample_user_model(sample_user_dict):
    return UserModel(**sample_user_dict)


@pytest.fixture
def auth_dto():
    return AuthenticationDTO(email="test@example.com", password="password123")


@pytest.mark.asyncio
async def test_get_user_by_email_found(user_service, user_collection, sample_user_dict):
    # Arrange
    user_collection.find_one.return_value = sample_user_dict

    # Act
    result = await user_service.get_user_by_email("test@example.com")

    # Assert
    assert result is not None
    assert result.email == "test@example.com"
    user_collection.find_one.assert_called_once_with({"email": "test@example.com"})


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(user_service, user_collection):
    # Arrange
    user_collection.find_one.return_value = None

    # Act
    result = await user_service.get_user_by_email("nonexistent@example.com")

    # Assert
    assert result is None
    user_collection.find_one.assert_called_once_with({"email": "nonexistent@example.com"})


@pytest.mark.asyncio
async def test_register_success(user_service, user_collection, auth_dto, sample_user_dict):
    # Arrange
    user_service.get_user_by_email = AsyncMock(return_value=None)
    user_collection.insert_one.return_value = MagicMock(inserted_id="user_id_123")
    user_collection.find_one.return_value = sample_user_dict

    # Act
    with patch("capstone.backend.app.services.user_service.get_password_hash", return_value="hashed_password123"):
        with patch("capstone.backend.app.services.user_service.create_jwt", return_value="jwt_token"):
            result = await user_service.register(auth_dto)

    # Assert
    assert result == "jwt_token"
    user_service.get_user_by_email.assert_called_once_with(auth_dto.email)
    user_collection.insert_one.assert_called_once()
    user_collection.find_one.assert_called_once_with({"_id": "user_id_123"})


@pytest.mark.asyncio
async def test_register_email_exists(user_service, auth_dto, sample_user_model):
    # Arrange
    user_service.get_user_by_email = AsyncMock(return_value=sample_user_model)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.register(auth_dto)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already exists"


@pytest.mark.asyncio
async def test_login_success(user_service, auth_dto, sample_user_model):
    # Arrange
    user_service.get_user_by_email = AsyncMock(return_value=sample_user_model)

    # Act
    with patch("capstone.backend.app.services.user_service.verify_password", return_value=True):
        with patch("capstone.backend.app.services.user_service.create_jwt", return_value="jwt_token"):
            result = await user_service.login(auth_dto)

    # Assert
    assert result == "jwt_token"
    user_service.get_user_by_email.assert_called_once_with(auth_dto.email)


@pytest.mark.asyncio
async def test_login_user_not_found(user_service, auth_dto):
    # Arrange
    user_service.get_user_by_email = AsyncMock(return_value=None)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.login(auth_dto)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email or Password is not correct!"


@pytest.mark.asyncio
async def test_login_incorrect_password(user_service, auth_dto, sample_user_model):
    # Arrange
    user_service.get_user_by_email = AsyncMock(return_value=sample_user_model)

    # Act & Assert
    with patch("capstone.backend.app.services.user_service.verify_password", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await user_service.login(auth_dto)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email or Password is not correct!"