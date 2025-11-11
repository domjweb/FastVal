from fastapi import APIRouter
from app.api.v1.endpoints import claims, remittance, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(claims.router, prefix="/claims", tags=["claims"])
api_router.include_router(remittance.router, prefix="/remittance", tags=["remittance"])
