from contextlib import asynccontextmanager
from fastapi import FastAPI
from schemas import create_tables
from routers import Todo, AuthApi, YoutubeMusic


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server Started!")
    create_tables()
    yield
    print("Server Exited.!")


app = FastAPI(
    title="Henry's API app",
    description="A sample fast api app.",
    lifespan=lifespan,
)


app.include_router(Todo.router, prefix="/todo")
app.include_router(AuthApi.router, prefix="/auth-api")
app.include_router(YoutubeMusic.router, prefix="/youtube-music")
