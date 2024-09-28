from api.v1 import registration
from core.config import auth_settings
from db import redis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

app = FastAPI(
    title=auth_settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = Redis.from_url(auth_settings.redis_dsn)


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()


app.include_router(registration.router, prefix="/api/v1", tags=["Registration"])
