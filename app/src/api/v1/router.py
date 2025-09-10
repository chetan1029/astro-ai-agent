from fastapi import APIRouter
from app.src.birthprofile.api import router as birthprofile_router
from app.src.healthcheck.api import router as healthcheck_router
from app.src.astroprofile.api import router as astroprofile_router
from app.src.interpretation.api import router as interpretation_router
from app.src.horoscope.api import router as horoscope_router
from app.src.whatsapp.api import router as whatsapp_router
from app.src.userprofile.api import router as userprofile_router

router = APIRouter()

router.include_router(
    birthprofile_router, prefix="/birth-profile", tags=["BirthProfile"]
)
router.include_router(
    astroprofile_router, prefix="/astro-profile", tags=["AstroProfile"]
)
router.include_router(
    interpretation_router, prefix="/interpretation", tags=["Interpretation"]
)
router.include_router(
    horoscope_router,
    prefix="/horoscope",
    tags=["Horoscope"],
)
router.include_router(whatsapp_router, prefix="/whatsapp", tags=["WhatsApp"])
router.include_router(userprofile_router, prefix="/user-profile", tags=["UserProfile"])
router.include_router(healthcheck_router, prefix="", tags=["HealthCheck"])
