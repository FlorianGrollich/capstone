from typing import List

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.params import Depends
from fastapi.responses import JSONResponse

from capstone.backend.app.core.config import settings
from capstone.backend.app.core.dependencies import get_video_service, get_current_user
from capstone.backend.app.schemas.project import Project
from capstone.backend.app.services.video_service import VideoService

from capstone.backend.app.utils.analyzer import run_video_analysis

router = APIRouter()


from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.params import Depends
from fastapi.responses import JSONResponse

@router.post("/upload")
async def upload_video_file(
    file: UploadFile = File(...),
    video_service: VideoService = Depends(get_video_service),
    user_payload: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    if not settings.bytescale_api_key or not settings.bytescale_account_id:
        raise HTTPException(status_code=500, detail="Server configuration error: Upload service credentials not set.")

    try:
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Cannot upload an empty file.")

        upload_metadata = {
            "originalFileName": file.filename,
            "contentType": file.content_type
        }
        upload_querystring = {
            "fileName": file.filename
        }

        user_email = user_payload.get("email")

        # Upload the video to Bytescale
        response_data = await video_service.upload_video(
            account_id=settings.bytescale_account_id,
            api_key=settings.bytescale_api_key,
            user_email=user_email,
            request_body=file_content,
            metadata=upload_metadata,
            querystring=upload_querystring
        )

        file_url = response_data.get("fileUrl")

        # Add video analysis as a background task using the URL
        background_tasks.add_task(
            analyze_and_update_video, file_url, video_service, user_email
        )

        return JSONResponse(content=response_data, status_code=200)

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An internal server error occurred during file processing.")

async def analyze_and_update_video(file_url: str, video_service: VideoService, user_email: str):
    """
    Background task to analyze the video using the URL directly and update MongoDB.
    """
    try:
        analysis_results = await run_video_analysis(file_url)
        new_url = file_url.replace("raw", "video")
        print("new url: ", new_url)
        stats = await video_service.finish_stats(new_url, analysis_results)
        print(stats)

    except Exception as e:
        # Log error and update status in MongoDB
        import logging
        logging.error(f"Error during video analysis: {e}")
        await video_service.video_collection.update_one(
            {"file_url": file_url},
            {"$set": {"status": "error", "error_message": str(e)}}
        )

@router.get("/projects")
async def get_projects(
        user_payload: dict = Depends(get_current_user),
        video_service: VideoService = Depends(get_video_service)) -> List[Project]:
    user_email = user_payload.get("email")
    projects = await video_service.get_projects(user_email)
    return projects


@router.get("/project/{id}")
async def get_project_by_id(
        id: str,
        user_payload: dict = Depends(get_current_user),
        video_service: VideoService = Depends(get_video_service)):
    user_email = user_payload.get("email")
    project = await video_service.get_video_stats(id, user_email)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
