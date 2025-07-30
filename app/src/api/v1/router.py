from fastapi import APIRouter
from app.src.birthprofile.api import router as birthprofile_router
from app.src.healthcheck.api import router as healthcheck_router
from app.src.astroprofile.api import router as astroprofile_router

router = APIRouter()

router.include_router(
    birthprofile_router, prefix="/birth-profile", tags=["BirthProfile"]
)
router.include_router(
    astroprofile_router, prefix="/astro-profile", tags=["AstroProfile"]
)
router.include_router(healthcheck_router, prefix="/healthcheck", tags=["HealthCheck"])
