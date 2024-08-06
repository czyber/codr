from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from codr.api.routers.github import router as github_router
from codr.api.routers.users import router as users_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=github_router, tags=["github"])
