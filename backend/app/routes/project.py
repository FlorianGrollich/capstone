from typing import List

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.params import Depends
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.depedencies import get_video_service, get_current_user
from app.schemas.project import Project
from app.services.video_service import VideoService

router = APIRouter()


@router.post("/upload")
async def upload_video_file(file: UploadFile = File(...),
                            video_service: VideoService = Depends(get_video_service),
                            user_payload: dict = Depends(get_current_user)
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

        response_data = await video_service.upload_video(
            account_id=settings.bytescale_account_id,
            api_key=settings.bytescale_api_key,
            user_email=user_email,
            request_body=file_content,
            metadata=upload_metadata,
            querystring=upload_querystring
        )

        return JSONResponse(content=response_data, status_code=200)

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An internal server error occurred during file processing.")


@router.get("/projects")
async def get_projects(
        user_payload: dict = Depends(get_current_user),
        video_service: VideoService = Depends(get_video_service)) -> List[Project]:
    user_email = user_payload.get("email")
    projects = await video_service.get_projects(user_email)
    return projects
