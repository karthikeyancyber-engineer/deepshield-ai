from fastapi import FastAPI, Request, Response, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import init_db
from app.routers import auth, interviews, admin, live, reports, otp_auth, interview_requests, notifications, video_stream, livekit
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("deepshield")

settings = get_settings()

APP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
FRONTEND_DIR = os.path.join(APP_DIR, "out")
uploads_dir = os.path.join(APP_DIR, "uploads")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting DeepShield AI v%s", settings.APP_VERSION)
    logger.info("RESEND_API_KEY set: %s", bool(settings.RESEND_API_KEY))
    logger.info("Frontend dir: %s (exists: %s)", FRONTEND_DIR, os.path.exists(FRONTEND_DIR))
    if os.path.exists(FRONTEND_DIR):
        logger.info("Frontend files: %s", os.listdir(FRONTEND_DIR)[:10])
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down DeepShield AI")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response()
        response.status_code = 204
    else:
        response = await call_next(request)

    origin = request.headers.get("origin", "*")
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response


api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(otp_auth.router)
api_router.include_router(interviews.router)
api_router.include_router(admin.router)
api_router.include_router(live.router)
api_router.include_router(reports.router)
api_router.include_router(interview_requests.router)
api_router.include_router(notifications.router)
api_router.include_router(video_stream.router)
api_router.include_router(livekit.router)

app.include_router(api_router)

os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/health")
async def health():
    import os
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "resend_key_set": bool(os.environ.get("RESEND_API_KEY")),
        "email_env_vars": [k for k in os.environ.keys() if "RESEND" in k or "EMAIL" in k or "resend" in k],
    }


next_static = os.path.join(FRONTEND_DIR, "_next")
if os.path.exists(next_static):
    app.mount("/_next", StaticFiles(directory=next_static), name="next-static")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api/"):
        return Response(status_code=404)

    if full_path.startswith("_next/"):
        file_path = os.path.join(FRONTEND_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return Response(status_code=404)

    if full_path:
        file_path = os.path.join(FRONTEND_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        if os.path.isfile(file_path + "/index.html"):
            return FileResponse(file_path + "/index.html")

        if os.path.isfile(file_path + ".html"):
            return FileResponse(file_path + ".html")

    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file)

    return Response(status_code=404)
