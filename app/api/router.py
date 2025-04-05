from fastapi import APIRouter

from app.api.v1.endpoints.spotlight_router import spotlight_router
from app.api.v1.endpoints.tag_labeling_api import tag_labeling_router
from app.api.v1.endpoints.test_router  import test_router
from app.api.v1.endpoints.healthcheck_router import healthcheck_router

api_router = APIRouter()

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(test_router, prefix="/test", tags=["Test"])
api_v1_router.include_router(healthcheck_router, prefix="/healthcheck", tags=["Healthcheck"])
api_v1_router.include_router(spotlight_router, prefix="/spotlight", tags=["Spotlight"])
api_v1_router.include_router(tag_labeling_router, prefix="/tag-labeling", tags=["Tag Labeling"])

api_router.include_router(api_v1_router)
