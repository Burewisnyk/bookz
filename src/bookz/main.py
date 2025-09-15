from fastapi import FastAPI
from contextlib import asynccontextmanager
from .db import close_db
from .repositories.init_db import init_db
from .routers.router import router
from .services.dto_models import NewDepositoryDTO

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(NewDepositoryDTO())
    yield
    close_db()

app = FastAPI(lifespan=lifespan)

app.include_router(router)