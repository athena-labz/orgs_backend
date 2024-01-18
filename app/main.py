from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.routers import users, organizations, tasks, groups
from app.lib import environment

import logging


DATABASE = environment.get("DATABASE")


logging.basicConfig(
    level=logging.INFO, format="%(filename)s:%(lineno)s %(levelname)s:%(message)s"
)

app = FastAPI()

app.include_router(users.router)
app.include_router(organizations.router)
app.include_router(tasks.router)
app.include_router(groups.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {}


register_tortoise(app, db_url=DATABASE, modules={"models": ["app.model"]})
