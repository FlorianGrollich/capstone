from fastapi import FastAPI
from app.routes.user import router

app = FastAPI()


app.include_router(router)

