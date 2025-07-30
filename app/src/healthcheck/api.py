import uuid

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import text

from app.src.core.db import get_session, async_session_maker

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}


@router.get("/db", status_code=status.HTTP_200_OK)
async def health_check_db():
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database connection failed")
