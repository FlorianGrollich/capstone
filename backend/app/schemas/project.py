from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class ProjectStatus(Enum):
    LOADING = "loading"
    ERROR = "error"
    FINISHED = "finished"


class Possession(BaseModel):
    team1: int
    team2: int

class Pass(BaseModel):
    team1: Optional[int] = None
    team2: Optional[int] = None

class StatEntry(BaseModel):
    POSSESSION: Optional[Possession] = None
    PASS: Optional[Pass] = None

class AnalysisResults(BaseModel):
    stats: Dict[str, StatEntry]

class Project(BaseModel):
    id: ObjectId = Field(alias="_id")
    email: List[str]
    file_url: str
    analysis_results: AnalysisResults
    status: ProjectStatus
    title: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ProjectSummary(BaseModel):
    id: ObjectId = Field(alias="_id")
    status: ProjectStatus
    title: str
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
