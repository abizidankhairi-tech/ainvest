from fastapi import APIRouter
from .auth import router as auth_router
from .portfolio import router as portfolio_router
from .holdings import router as holdings_router
from .stocks import router as stocks_router
from .ai import router as ai_router
from .strategies import router as strategies_router
from .alerts import router as alerts_router
from .import_portfolio import router as import_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(portfolio_router)
api_router.include_router(holdings_router)
api_router.include_router(stocks_router)
api_router.include_router(ai_router)
api_router.include_router(strategies_router)
api_router.include_router(alerts_router)
api_router.include_router(import_router)
