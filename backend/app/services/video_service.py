import httpx
import json

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from app.schemas.project import Project, ProjectState


class VideoService:

    def __init__(self, video_collection: AsyncIOMotorCollection):
        self.video_collection = video_collection

    async def upload_video(self,
                           account_id: str,
                           user_email: str,
                           api_key: str, request_body: bytes,
                           metadata: dict | None = None,
                           querystring: dict | None = None):
        base_url = "https://api.bytescale.com"
        path = f"/v2/accounts/{account_id}/uploads/binary"
        url = f"{base_url}{path}"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/octet-stream"
        }
        if metadata:
            try:
                headers["X-Upload-Metadata"] = json.dumps(metadata)
            except TypeError as e:
                raise ValueError(f"Metadata could not be serialized to JSON: {metadata}") from e

        params_to_send = querystring if querystring is not None else {}

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    params=params_to_send,
                    content=request_body
                )
                response.raise_for_status()

                file_url = response.json()["fileUrl"]
                print(file_url)
                print(user_email)
                await self.video_collection.insert_one({
                    "email": [user_email],
                    "file_url": file_url
                })

                return response.json()
            except httpx.RequestError as exc:
                raise HTTPException(status_code=503, detail=f"Error connecting to upload service: {type(exc).__name__}")
            except httpx.HTTPStatusError as exc:
                error_detail = f"Upload service error ({exc.response.status_code})"
                try:
                    api_error = exc.response.json()
                    if isinstance(api_error, dict) and 'error' in api_error and isinstance(api_error['error'], dict):
                        error_detail = api_error['error'].get('message', error_detail)
                    else:
                        error_detail = f"{error_detail}: {exc.response.text[:200]}"
                except (json.JSONDecodeError, AttributeError, TypeError):
                    error_detail = f"{error_detail}: {exc.response.text[:200]}"
                raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
            except ValueError as ve:
                raise HTTPException(status_code=400, detail=str(ve))

    async def get_projects(self, user_email):
        return [
            Project(video_url="https://upcdn.io/.../annotated_video(1)(1)(1).mp4",
                    title="Test title",
                    state=ProjectState.FINISHED),
            Project(video_url="https://upcdn.io/.../annotated_video(1)(1)(1).mp4",
                    title="Test title",
                    state=ProjectState.LOADING),
            Project(video_url="https://upcdn.io/.../annotated_video(1)(1)(1).mp4",
                    title="Test title",
                    state=ProjectState.ERROR),
        ]

    async def get_video_stats(self, id, user_email):
        return {
            "video_url": "https://upcdn.io/.../annotated_video(1)(1)(1).mp4",
            "stats": {
                "850": {
                    "POSSESSION": {
                        "team1": 33,
                        "team2": 67
                    },
                    "PASS": {
                        "team1": 6,
                        "team2": 3
                    }
                },
                "2300": {
                    "POSSESSION": {
                        "team1": 36,
                        "team2": 64
                    },
                    "PASS": {
                        "team1": 9,
                        "team2": 4
                    }
                },
                "3870": {
                    "POSSESSION": {
                        "team1": 40,
                        "team2": 60
                    },
                    "PASS": {
                        "team1": 11,
                        "team2": 6
                    }
                },
                "4890": {
                    "PASS": {
                        "team1": 13,
                        "team2": 9
                    }
                },
                "5630": {
                    "POSSESSION": {
                        "team1": 43,
                        "team2": 57
                    }
                },
                "6420": {
                    "PASS": {
                        "team1": 15
                    }
                },
                "7150": {
                    "PASS": {
                        "team2": 11
                    }
                },
                "8030": {
                    "POSSESSION": {
                        "team1": 46,
                        "team2": 54
                    },
                    "PASS": {
                        "team1": 16
                    }
                },
                "9020": {
                    "POSSESSION": {
                        "team1": 48,
                        "team2": 52
                    },
                    "PASS": {
                        "team2": 13
                    }
                },
                "10010": {
                    "PASS": {
                        "team1": 18,
                        "team2": 14
                    }
                },
                "11250": {
                    "POSSESSION": {
                        "team1": 50,
                        "team2": 50
                    },
                    "PASS": {
                        "team1": 20
                    }
                },
                "12680": {
                    "PASS": {
                        "team2": 16
                    }
                }
            }
        }
