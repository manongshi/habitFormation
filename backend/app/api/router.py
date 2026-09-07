from fastapi import APIRouter

from app.api.routes import auth, certificates, dashboard, goals, health, payments, study_plans

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(certificates.router)
api_router.include_router(goals.router)
api_router.include_router(dashboard.router)
api_router.include_router(payments.router)
api_router.include_router(study_plans.router)
