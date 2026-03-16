from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from database import get_db
from models.user import User
from models.portfolio import Portfolio
from models.holding import Holding
from models.ai_query import AIQuery
from models.ai_recommendation import AIRecommendation
from api.auth import get_current_user
from services.ai_service import ai_service
from services.stock_service import stock_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


# Pydantic models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = None
    include_portfolio: bool = True


class ChatResponse(BaseModel):
    response: str
    tokens_used: int
    response_time_ms: int
    error: bool = False


class AnalysisRequest(BaseModel):
    analysis_type: str  # "portfolio", "stock", "entry_strategy"
    symbol: Optional[str] = None
    capital: Optional[float] = None


class InsightResponse(BaseModel):
    type: str  # "warning", "opportunity", "info"
    title: str
    description: str


def get_portfolio_with_prices(user_id: int, db: Session) -> tuple:
    """Helper to get portfolio holdings with current prices"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.user_id == user_id,
        Portfolio.is_active == True
    ).first()
    
    if not portfolio:
        return None, []
    
    holdings = db.query(Holding).filter(
        Holding.portfolio_id == portfolio.id
    ).all()
    
    if not holdings:
        return portfolio, []
    
    # Get current prices
    symbols = [h.symbol for h in holdings]
    prices = stock_service.get_multiple_prices(symbols)
    
    holdings_data = []
    for h in holdings:
        symbol = h.symbol
        current_price = float(h.avg_cost)
        
        if symbol in prices:
            current_price = prices[symbol].get('price', current_price)
        
        market_value = h.shares * current_price
        cost = h.shares * float(h.avg_cost)
        gain_loss = market_value - cost
        gain_loss_pct = (gain_loss / cost * 100) if cost > 0 else 0
        
        holdings_data.append({
            "symbol": symbol,
            "shares": h.shares,
            "avg_cost": float(h.avg_cost),
            "current_price": current_price,
            "market_value": market_value,
            "cost": cost,
            "gain_loss": gain_loss,
            "gain_loss_pct": gain_loss_pct,
            "sector": h.sector or "Unknown"
        })
    
    return portfolio, holdings_data


@router.post("/chat", response_model=ChatResponse)
def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with AI assistant about investing"""
    
    # Get portfolio context if requested
    portfolio_context = None
    portfolio = None
    
    if request.include_portfolio:
        portfolio, holdings_data = get_portfolio_with_prices(current_user.id, db)
        if holdings_data:
            portfolio_context = {"holdings": holdings_data}
    
    # Convert conversation history
    history = None
    if request.conversation_history:
        history = [{"role": m.role, "content": m.content} for m in request.conversation_history]
    
    # Get AI response
    result = ai_service.chat(
        message=request.message,
        conversation_history=history,
        portfolio_context=portfolio_context
    )
    
    # Save query to database
    try:
        ai_query = AIQuery(
            user_id=current_user.id,
            portfolio_id=portfolio.id if portfolio else None,
            query_text=request.message,
            response_text=result.get("response", ""),
            context=portfolio_context,
            tokens_used=result.get("tokens_used", 0),
            response_time_ms=result.get("response_time_ms", 0)
        )
        db.add(ai_query)
        db.commit()
    except Exception as e:
        print(f"Error saving AI query: {e}")
    
    return ChatResponse(
        response=result.get("response", ""),
        tokens_used=result.get("tokens_used", 0),
        response_time_ms=result.get("response_time_ms", 0),
        error=result.get("error", False)
    )


@router.post("/analyze", response_model=ChatResponse)
def analyze(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI analysis for portfolio or specific stock"""
    
    portfolio, holdings_data = get_portfolio_with_prices(current_user.id, db)
    
    if request.analysis_type == "portfolio":
        result = ai_service.analyze_portfolio(holdings_data)
        
    elif request.analysis_type == "stock":
        if not request.symbol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Symbol is required for stock analysis"
            )
        result = ai_service.get_stock_analysis(request.symbol, holdings_data)
        
    elif request.analysis_type == "entry_strategy":
        if not request.symbol or not request.capital:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Symbol and capital are required for entry strategy"
            )
        result = ai_service.get_entry_strategy(request.symbol, request.capital, holdings_data)
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis type. Use: portfolio, stock, or entry_strategy"
        )
    
    # Save query to database
    try:
        ai_query = AIQuery(
            user_id=current_user.id,
            portfolio_id=portfolio.id if portfolio else None,
            query_text=f"[{request.analysis_type.upper()}] {request.symbol or 'Portfolio'}",
            response_text=result.get("response", ""),
            context={"holdings": holdings_data} if holdings_data else None,
            tokens_used=result.get("tokens_used", 0),
            response_time_ms=result.get("response_time_ms", 0)
        )
        db.add(ai_query)
        db.commit()
    except Exception as e:
        print(f"Error saving AI query: {e}")
    
    return ChatResponse(
        response=result.get("response", ""),
        tokens_used=result.get("tokens_used", 0),
        response_time_ms=result.get("response_time_ms", 0),
        error=result.get("error", False)
    )


@router.get("/insights", response_model=List[InsightResponse])
def get_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quick AI insights for dashboard"""
    
    portfolio, holdings_data = get_portfolio_with_prices(current_user.id, db)
    
    insights = ai_service.get_quick_insights(holdings_data)
    
    return [InsightResponse(**i) for i in insights]


@router.get("/history")
def get_ai_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's AI query history"""
    
    queries = db.query(AIQuery).filter(
        AIQuery.user_id == current_user.id
    ).order_by(AIQuery.created_at.desc()).limit(limit).all()
    
    return [{
        "id": q.id,
        "query": q.query_text,
        "response": q.response_text[:500] + "..." if len(q.response_text) > 500 else q.response_text,
        "tokens_used": q.tokens_used,
        "response_time_ms": q.response_time_ms,
        "created_at": q.created_at.isoformat() if q.created_at else None
    } for q in queries]


@router.post("/feedback/{query_id}")
def submit_feedback(
    query_id: int,
    satisfied: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for an AI response"""
    
    query = db.query(AIQuery).filter(
        AIQuery.id == query_id,
        AIQuery.user_id == current_user.id
    ).first()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    query.satisfied = satisfied
    db.commit()
    
    return {"message": "Feedback submitted", "satisfied": satisfied}
