from fastapi import APIRouter

from app.api.v1.endpoints.test_router  import test_router
from app.api.v1.endpoints.healthcheck_router import healthcheck_router

api_router = APIRouter()

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(test_router, prefix="/test", tags=["Test"])
api_v1_router.include_router(healthcheck_router, prefix="/healthcheck", tags=["Healthcheck"])

api_router.include_router(api_v1_router)
