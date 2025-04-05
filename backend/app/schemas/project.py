from pydantic import BaseModel


class Project(BaseModel):
    video_url: str
    title: str