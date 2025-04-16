import httpx
import json

from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from capstone.backend.app.schemas.project import Project, ProjectStatus, ProjectSummary


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
            "Content-Type": "video/mp4"
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

                file_path = response.json()["filePath"]
                file_url = f"https://upcdn.io/{account_id}/video{file_path}"
                title = file_path.split("/")[-1]
                print(file_url)
                print(user_email)
                await self.video_collection.insert_one({
                    "email": [user_email],
                    "file_url": file_url,
                    "status": "loading",
                    "title": title
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

    async def update_status(self, file_url):
        await self.video_collection.update_one(
            {"file_url": file_url},
            {"$set": {"status": "processing"}}
        )

    async def finish_stats(self, file_url: str, stats: dict):
        print(f"calling finish stats: {file_url}")
        file_url.replace("raw", "video")
        try:
            test = await self.video_collection.update_one(
                {"file_url": file_url},
                {"$set": {"status": "finished", "analysis_results": stats}}
            )
            print(test)
        except Exception as e:
            print(f"Error on finish stats: {e}")

    async def get_projects(self, user_email: str) -> list[ProjectSummary]:
        cursor = self.video_collection.find({"email": [user_email]})
        projects = []
        documents = await cursor.to_list(length=None)
        for doc in documents:
            projects.append(ProjectSummary(title=doc.get("title"), status=doc.get("status"), _id=doc.get("_id")))

        return projects

    async def get_video_stats(self, project_id: str, user_email: str):
        project = await self.video_collection.find_one({"_id": ObjectId(project_id), "email": [user_email]})
        if not project:
            return None

        return Project(**project)
