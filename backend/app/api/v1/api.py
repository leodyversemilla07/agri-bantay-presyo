from fastapi import APIRouter
from app.api.v1.endpoints import commodities, markets, prices, trends, stats

api_router = APIRouter()
api_router.include_router(commodities.router, prefix="/commodities", tags=["commodities"])
api_router.include_router(markets.router, prefix="/markets", tags=["markets"])
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
api_router.include_router(trends.router, prefix="/trends", tags=["trends"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
