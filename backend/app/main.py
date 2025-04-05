from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routes import user, project

app = FastAPI()

origins = [
    "*",  # Common Vite/React development port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True,  # Allows cookies/authorization headers (important for auth)
    allow_methods=["*"],  # Allows all standard HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)
app.include_router(user.router)
app.include_router(video.router)
