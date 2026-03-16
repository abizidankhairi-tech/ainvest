from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from services.stock_service import stock_service
from api.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


class StockPriceResponse(BaseModel):
    symbol: str
    price: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None
    change: float = 0
    change_pct: float = 0
    timestamp: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    source: Optional[str] = None


class StockSearchResult(BaseModel):
    symbol: str
    name: str
    exchange: str


class StockHistoryItem(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


@router.get("/price/{symbol}", response_model=StockPriceResponse)
def get_stock_price(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Get current price for a stock"""
    price_data = stock_service.get_stock_price(symbol)
    
    if not price_data:
        raise HTTPException(
            status_code=404,
            detail=f"Stock {symbol} not found or price unavailable"
        )
    
    return price_data


@router.get("/prices", response_model=dict)
def get_multiple_prices(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    current_user: User = Depends(get_current_user)
):
    """Get prices for multiple stocks"""
    symbol_list = [s.strip() for s in symbols.split(",")]
    
    if len(symbol_list) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 symbols allowed per request"
        )
    
    prices = stock_service.get_multiple_prices(symbol_list)
    
    return {"prices": prices}


@router.get("/search", response_model=List[StockSearchResult])
def search_stocks(
    q: str = Query(..., min_length=1, description="Search query"),
    current_user: User = Depends(get_current_user)
):
    """Search for stocks by symbol or name"""
    results = stock_service.search_stocks(q)
    return results


@router.get("/history/{symbol}", response_model=List[StockHistoryItem])
def get_stock_history(
    symbol: str,
    period: str = Query("1mo", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y"),
    current_user: User = Depends(get_current_user)
):
    """Get historical price data for a stock"""
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd", "max"]
    
    if period not in valid_periods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period. Valid options: {', '.join(valid_periods)}"
        )
    
    history = stock_service.get_stock_history(symbol, period)
    
    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"History for {symbol} not found"
        )
    
    return history


@router.post("/refresh/{symbol}", response_model=StockPriceResponse)
def refresh_stock_price(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Force refresh price for a stock (bypass cache)"""
    price_data = stock_service.get_stock_price(symbol, force_refresh=True)
    
    if not price_data:
        raise HTTPException(
            status_code=404,
            detail=f"Stock {symbol} not found or price unavailable"
        )
    
    return price_data


@router.post("/refresh-all", response_model=dict)
def refresh_all_prices(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    current_user: User = Depends(get_current_user)
):
    """Force refresh prices for multiple stocks"""
    symbol_list = [s.strip() for s in symbols.split(",")]
    
    if len(symbol_list) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 symbols allowed per request"
        )
    
    prices = stock_service.refresh_all_prices(symbol_list)
    
    return {"prices": prices, "refreshed": len(prices)}
