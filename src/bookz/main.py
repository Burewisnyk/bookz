from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from .db import close_db
from .repositories.init_db import init_db
from .routers.router import router
from .services.dto_models import NewDepositoryDTO
from .logger import app_logger

app_logger.info("Start main module")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("Starting initialize project database...")
    init_db()
    app_logger.info("Initialization complete.")
    yield
    close_db()
    app_logger.info("Database close complete.")

app = FastAPI(
    title="Depository API",
    description="API for managing depositories",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api", tags=["api"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    app_logger.exception("Unhandled exception occurred: %s", exc)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "path": request.url.path
        },
    )