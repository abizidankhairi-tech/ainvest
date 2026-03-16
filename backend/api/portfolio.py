from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
from models.user import User
from models.portfolio import Portfolio
from api.auth import get_current_user

router = APIRouter(prefix="/api/portfolios", tags=["portfolios"])


# Pydantic models
class PortfolioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    base_currency: str = "IDR"


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PortfolioResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    is_active: bool
    base_currency: str

    class Config:
        from_attributes = True


class PortfolioWithSummary(PortfolioResponse):
    total_value: float = 0
    total_cost: float = 0
    unrealized_gain: float = 0
    unrealized_gain_pct: float = 0
    holdings_count: int = 0


@router.get("/", response_model=List[PortfolioResponse])
def get_portfolios(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all portfolios for the current user"""
    portfolios = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id
    ).all()
    
    return portfolios


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new portfolio"""
    new_portfolio = Portfolio(
        user_id=current_user.id,
        name=portfolio_data.name,
        description=portfolio_data.description,
        base_currency=portfolio_data.base_currency
    )
    
    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)
    
    return new_portfolio


@router.get("/{portfolio_id}", response_model=PortfolioWithSummary)
def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific portfolio with summary"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    # Calculate summary (will be enhanced later with real prices)
    total_cost = sum(float(h.shares * h.avg_cost) for h in portfolio.holdings)
    total_value = total_cost  # TODO: Update with real-time prices
    unrealized_gain = total_value - total_cost
    unrealized_gain_pct = (unrealized_gain / total_cost * 100) if total_cost > 0 else 0
    
    return {
        **portfolio.__dict__,
        "total_value": total_value,
        "total_cost": total_cost,
        "unrealized_gain": unrealized_gain,
        "unrealized_gain_pct": unrealized_gain_pct,
        "holdings_count": len(portfolio.holdings)
    }


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: int,
    portfolio_data: PortfolioUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a portfolio"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    if portfolio_data.name is not None:
        portfolio.name = portfolio_data.name
    if portfolio_data.description is not None:
        portfolio.description = portfolio_data.description
    if portfolio_data.is_active is not None:
        portfolio.is_active = portfolio_data.is_active
    
    db.commit()
    db.refresh(portfolio)
    
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a portfolio"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    db.delete(portfolio)
    db.commit()
    
    return None
