from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from database import get_db
from models.user import User
from models.portfolio import Portfolio
from models.holding import Holding
from models.transaction import Transaction
from api.auth import get_current_user
from datetime import date

router = APIRouter(prefix="/api/portfolios/{portfolio_id}/holdings", tags=["holdings"])


# Pydantic models
class HoldingCreate(BaseModel):
    symbol: str
    shares: int
    avg_cost: float
    sector: Optional[str] = None
    industry: Optional[str] = None


class HoldingUpdate(BaseModel):
    shares: Optional[int] = None
    avg_cost: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None


class HoldingResponse(BaseModel):
    id: int
    portfolio_id: int
    symbol: str
    shares: int
    avg_cost: float
    sector: Optional[str]
    industry: Optional[str]
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    unrealized_gain: Optional[float] = None
    unrealized_gain_pct: Optional[float] = None

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    transaction_type: str  # BUY or SELL
    symbol: str
    shares: int
    price: float
    fees: float = 0
    transaction_date: date
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    portfolio_id: int
    holding_id: Optional[int]
    transaction_type: str
    symbol: str
    shares: int
    price: float
    total_amount: float
    fees: float
    transaction_date: date
    notes: Optional[str]

    class Config:
        from_attributes = True


def verify_portfolio_ownership(portfolio_id: int, user: User, db: Session) -> Portfolio:
    """Helper to verify user owns the portfolio"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    return portfolio


@router.get("/", response_model=List[HoldingResponse])
def get_holdings(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all holdings for a portfolio"""
    verify_portfolio_ownership(portfolio_id, current_user, db)
    
    holdings = db.query(Holding).filter(
        Holding.portfolio_id == portfolio_id
    ).all()
    
    # Convert holdings to response format with calculations
    result = []
    for h in holdings:
        holding_dict = {
            "id": h.id,
            "portfolio_id": h.portfolio_id,
            "symbol": h.symbol,
            "shares": h.shares,
            "avg_cost": float(h.avg_cost),
            "sector": h.sector,
            "industry": h.industry,
            "current_price": None,  # TODO: Get from price service
            "market_value": None,
            "unrealized_gain": None,
            "unrealized_gain_pct": None
        }
        result.append(holding_dict)
    
    return result


@router.post("/", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
def create_holding(
    portfolio_id: int,
    holding_data: HoldingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new holding to the portfolio"""
    verify_portfolio_ownership(portfolio_id, current_user, db)
    
    # Check if holding already exists
    existing = db.query(Holding).filter(
        Holding.portfolio_id == portfolio_id,
        Holding.symbol == holding_data.symbol.upper()
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Holding for {holding_data.symbol.upper()} already exists. Use PUT to update."
        )
    
    new_holding = Holding(
        portfolio_id=portfolio_id,
        symbol=holding_data.symbol.upper(),
        shares=holding_data.shares,
        avg_cost=holding_data.avg_cost,
        sector=holding_data.sector,
        industry=holding_data.industry
    )
    
    db.add(new_holding)
    db.commit()
    db.refresh(new_holding)
    
    return {
        "id": new_holding.id,
        "portfolio_id": new_holding.portfolio_id,
        "symbol": new_holding.symbol,
        "shares": new_holding.shares,
        "avg_cost": float(new_holding.avg_cost),
        "sector": new_holding.sector,
        "industry": new_holding.industry
    }


@router.put("/{holding_id}", response_model=HoldingResponse)
def update_holding(
    portfolio_id: int,
    holding_id: int,
    holding_data: HoldingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a holding"""
    verify_portfolio_ownership(portfolio_id, current_user, db)
    
    holding = db.query(Holding).filter(
        Holding.id == holding_id,
        Holding.portfolio_id == portfolio_id
    ).first()
    
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holding not found"
        )
    
    if holding_data.shares is not None:
        holding.shares = holding_data.shares
    if holding_data.avg_cost is not None:
        holding.avg_cost = holding_data.avg_cost
    if holding_data.sector is not None:
        holding.sector = holding_data.sector
    if holding_data.industry is not None:
        holding.industry = holding_data.industry
    
    db.commit()
    db.refresh(holding)
    
    return {
        "id": holding.id,
        "portfolio_id": holding.portfolio_id,
        "symbol": holding.symbol,
        "shares": holding.shares,
        "avg_cost": float(holding.avg_cost),
        "sector": holding.sector,
        "industry": holding.industry
    }


@router.delete("/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(
    portfolio_id: int,
    holding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a holding"""
    verify_portfolio_ownership(portfolio_id, current_user, db)
    
    holding = db.query(Holding).filter(
        Holding.id == holding_id,
        Holding.portfolio_id == portfolio_id
    ).first()
    
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holding not found"
        )
    
    db.delete(holding)
    db.commit()
    
    return None


# Transaction endpoints
@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def record_transaction(
    portfolio_id: int,
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a buy/sell transaction and update holdings"""
    verify_portfolio_ownership(portfolio_id, current_user, db)
    
    symbol = transaction_data.symbol.upper()
    total_amount = transaction_data.shares * transaction_data.price + transaction_data.fees
    
    # Find or create holding
    holding = db.query(Holding).filter(
        Holding.portfolio_id == portfolio_id,
        Holding.symbol == symbol
    ).first()
    
    if transaction_data.transaction_type.upper() == "BUY":
        if holding:
            # Update average cost
            old_total = holding.shares * float(holding.avg_cost)
            new_total = transaction_data.shares * transaction_data.price
            new_shares = holding.shares + transaction_data.shares
            holding.avg_cost = (old_total + new_total) / new_shares
            holding.shares = new_shares
        else:
            # Create new holding
            holding = Holding(
                portfolio_id=portfolio_id,
                symbol=symbol,
                shares=transaction_data.shares,
                avg_cost=transaction_data.price
            )
            db.add(holding)
            db.flush()
    
    elif transaction_data.transaction_type.upper() == "SELL":
        if not holding or holding.shares < transaction_data.shares:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient shares to sell"
            )
        holding.shares -= transaction_data.shares
        
        # Remove holding if no shares left
        if holding.shares == 0:
            db.delete(holding)
            holding = None
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction type must be BUY or SELL"
        )
    
    # Create transaction record
    transaction = Transaction(
        portfolio_id=portfolio_id,
        holding_id=holding.id if holding else None,
        transaction_type=transaction_data.transaction_type.upper(),
        symbol=symbol,
        shares=transaction_data.shares,
        price=transaction_data.price,
        total_amount=total_amount,
        fees=transaction_data.fees,
        transaction_date=transaction_data.transaction_date,
        notes=transaction_data.notes
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return {
        "id": transaction.id,
        "portfolio_id": transaction.portfolio_id,
        "holding_id": transaction.holding_id,
        "transaction_type": transaction.transaction_type,
        "symbol": transaction.symbol,
        "shares": transaction.shares,
        "price": float(transaction.price),
        "total_amount": float(transaction.total_amount),
        "fees": float(transaction.fees),
        "transaction_date": transaction.transaction_date,
        "notes": transaction.notes
    }


@router.get("/transactions", response_model=List[TransactionResponse])
def get_transactions(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all transactions for a portfolio"""
    verify_portfolio_ownership(portfolio_id, current_user, db)
    
    transactions = db.query(Transaction).filter(
        Transaction.portfolio_id == portfolio_id
    ).order_by(Transaction.transaction_date.desc()).all()
    
    result = []
    for t in transactions:
        result.append({
            "id": t.id,
            "portfolio_id": t.portfolio_id,
            "holding_id": t.holding_id,
            "transaction_type": t.transaction_type,
            "symbol": t.symbol,
            "shares": t.shares,
            "price": float(t.price),
            "total_amount": float(t.total_amount),
            "fees": float(t.fees),
            "transaction_date": t.transaction_date,
            "notes": t.notes
        })
    
    return result
