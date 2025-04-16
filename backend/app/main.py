from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from capstone.backend.app.routes import user, project

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user.router)
app.include_router(project.router)
