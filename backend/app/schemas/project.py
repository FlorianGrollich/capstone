from enum import Enum

from pydantic import BaseModel


class ProjectState(Enum):
    LOADING = "loading"
    ERROR = "error"
    FINISHED = "finished"


class Project(BaseModel):
    video_url: str
    title: str
    state: ProjectState
