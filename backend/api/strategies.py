from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from database import get_db
from models.user import User
from models.portfolio import Portfolio
from models.holding import Holding
from models.entry_strategy import EntryStrategy
from models.exit_strategy import ExitStrategy
from models.strategy_execution import StrategyExecution
from api.auth import get_current_user
from services.stock_service import stock_service

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


# Pydantic models
class BuyZone(BaseModel):
    zone_num: int
    min_price: float
    max_price: float
    allocation: float  # Percentage of total capital


class EntryStrategyCreate(BaseModel):
    symbol: str
    buy_zones: List[BuyZone]
    total_capital: float
    alert_enabled: bool = True


class EntryStrategyResponse(BaseModel):
    id: int
    portfolio_id: int
    symbol: str
    buy_zones: List[dict]
    total_capital: float
    deployed_capital: float
    status: str
    alert_enabled: bool
    current_price: Optional[float] = None
    
    class Config:
        from_attributes = True


class ExitStrategyCreate(BaseModel):
    holding_id: int
    tp1_price: Optional[float] = None
    tp1_allocation: Optional[float] = None  # Percentage to sell
    tp2_price: Optional[float] = None
    tp2_allocation: Optional[float] = None
    tp3_price: Optional[float] = None
    tp3_allocation: Optional[float] = None
    stop_loss: Optional[float] = None
    alert_enabled: bool = True


class ExitStrategyResponse(BaseModel):
    id: int
    holding_id: int
    symbol: str
    tp1_price: Optional[float]
    tp1_allocation: Optional[float]
    tp2_price: Optional[float]
    tp2_allocation: Optional[float]
    tp3_price: Optional[float]
    tp3_allocation: Optional[float]
    stop_loss: Optional[float]
    alert_enabled: bool
    current_price: Optional[float] = None
    avg_cost: Optional[float] = None
    
    class Config:
        from_attributes = True


class StrategyExecutionCreate(BaseModel):
    entry_strategy_id: int
    execution_type: str  # BUY or SELL
    zone_num: Optional[int] = None
    shares: int
    price: float
    execution_date: date
    notes: Optional[str] = None


def get_user_portfolio(user_id: int, db: Session) -> Portfolio:
    """Get user's active portfolio"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.user_id == user_id,
        Portfolio.is_active == True
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active portfolio found"
        )
    
    return portfolio


# Entry Strategy Endpoints

@router.get("/entry", response_model=List[EntryStrategyResponse])
def get_entry_strategies(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all entry strategies for the user"""
    portfolio = get_user_portfolio(current_user.id, db)
    
    query = db.query(EntryStrategy).filter(
        EntryStrategy.portfolio_id == portfolio.id
    )
    
    if status_filter:
        query = query.filter(EntryStrategy.status == status_filter)
    
    strategies = query.order_by(EntryStrategy.created_at.desc()).all()
    
    # Get current prices
    symbols = list(set([s.symbol for s in strategies]))
    prices = stock_service.get_multiple_prices(symbols) if symbols else {}
    
    result = []
    for s in strategies:
        current_price = None
        if s.symbol in prices:
            current_price = prices[s.symbol].get('price')
        
        result.append({
            "id": s.id,
            "portfolio_id": s.portfolio_id,
            "symbol": s.symbol,
            "buy_zones": s.buy_zones,
            "total_capital": float(s.total_capital),
            "deployed_capital": float(s.deployed_capital) if s.deployed_capital else 0,
            "status": s.status,
            "alert_enabled": s.alert_enabled,
            "current_price": current_price
        })
    
    return result


@router.post("/entry", response_model=EntryStrategyResponse, status_code=status.HTTP_201_CREATED)
def create_entry_strategy(
    strategy: EntryStrategyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new entry strategy"""
    portfolio = get_user_portfolio(current_user.id, db)
    
    # Validate buy zones allocations sum to 100%
    total_allocation = sum(zone.allocation for zone in strategy.buy_zones)
    if abs(total_allocation - 100) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Buy zone allocations must sum to 100% (got {total_allocation}%)"
        )
    
    # Convert buy zones to JSON-serializable format
    buy_zones_data = [
        {
            "zone_num": zone.zone_num,
            "min_price": zone.min_price,
            "max_price": zone.max_price,
            "allocation": zone.allocation
        }
        for zone in strategy.buy_zones
    ]
    
    new_strategy = EntryStrategy(
        portfolio_id=portfolio.id,
        symbol=strategy.symbol.upper(),
        buy_zones=buy_zones_data,
        total_capital=strategy.total_capital,
        deployed_capital=0,
        status='active',
        alert_enabled=strategy.alert_enabled
    )
    
    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)
    
    # Get current price
    current_price = None
    price_data = stock_service.get_stock_price(strategy.symbol)
    if price_data:
        current_price = price_data.get('price')
    
    return {
        "id": new_strategy.id,
        "portfolio_id": new_strategy.portfolio_id,
        "symbol": new_strategy.symbol,
        "buy_zones": new_strategy.buy_zones,
        "total_capital": float(new_strategy.total_capital),
        "deployed_capital": 0,
        "status": new_strategy.status,
        "alert_enabled": new_strategy.alert_enabled,
        "current_price": current_price
    }


@router.get("/entry/{strategy_id}", response_model=EntryStrategyResponse)
def get_entry_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific entry strategy"""
    portfolio = get_user_portfolio(current_user.id, db)
    
    strategy = db.query(EntryStrategy).filter(
        EntryStrategy.id == strategy_id,
        EntryStrategy.portfolio_id == portfolio.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry strategy not found"
        )
    
    # Get current price
    current_price = None
    price_data = stock_service.get_stock_price(strategy.symbol)
    if price_data:
        current_price = price_data.get('price')
    
    return {
        "id": strategy.id,
        "portfolio_id": strategy.portfolio_id,
        "symbol": strategy.symbol,
        "buy_zones": strategy.buy_zones,
        "total_capital": float(strategy.total_capital),
        "deployed_capital": float(strategy.deployed_capital) if strategy.deployed_capital else 0,
        "status": strategy.status,
        "alert_enabled": strategy.alert_enabled,
        "current_price": current_price
    }


@router.put("/entry/{strategy_id}")
def update_entry_strategy(
    strategy_id: int,
    status_update: Optional[str] = None,
    alert_enabled: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an entry strategy"""
    portfolio = get_user_portfolio(current_user.id, db)
    
    strategy = db.query(EntryStrategy).filter(
        EntryStrategy.id == strategy_id,
        EntryStrategy.portfolio_id == portfolio.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry strategy not found"
        )
    
    if status_update:
        if status_update not in ['active', 'completed', 'cancelled']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Use: active, completed, or cancelled"
            )
        strategy.status = status_update
    
    if alert_enabled is not None:
        strategy.alert_enabled = alert_enabled
    
    db.commit()
    
    return {"message": "Strategy updated successfully"}


@router.delete("/entry/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an entry strategy"""
    portfolio = get_user_portfolio(current_user.id, db)
    
    strategy = db.query(EntryStrategy).filter(
        EntryStrategy.id == strategy_id,
        EntryStrategy.portfolio_id == portfolio.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry strategy not found"
        )
    
    db.delete(strategy)
    db.commit()
    
    return None


# Exit Strategy Endpoints

@router.get("/exit", response_model=List[ExitStrategyResponse])
def get_exit_strategies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all exit strategies for user's holdings"""
    portfolio = get_user_portfolio(current_user.id, db)
    
    # Get holdings with exit strategies
    holdings = db.query(Holding).filter(
        Holding.portfolio_id == portfolio.id
    ).all()
    
    holding_ids = [h.id for h in holdings]
    
    strategies = db.query(ExitStrategy).filter(
        ExitStrategy.holding_id.in_(holding_ids)
    ).all()
    
    # Get current prices
    symbols = list(set([s.symbol for s in strategies]))
    prices = stock_service.get_multiple_prices(symbols) if symbols else {}
    
    # Build holding map for avg cost
    holding_map = {h.id: h for h in holdings}
    
    result = []
    for s in strategies:
        current_price = None
        if s.symbol in prices:
            current_price = prices[s.symbol].get('price')
        
        holding = holding_map.get(s.holding_id)
        avg_cost = float(holding.avg_cost) if holding else None
        
        result.append({
            "id": s.id,
            "holding_id": s.holding_id,
            "symbol": s.symbol,
            "tp1_price": float(s.tp1_price) if s.tp1_price else None,
            "tp1_allocation": float(s.tp1_allocation) if s.tp1_allocation else None,
            "tp2_price": float(s.tp2_price) if s.tp2_price else None,
            "tp2_allocation": float(s.tp2_allocation) if s.tp2_allocation else None,
            "tp3_price": float(s.tp3_price) if s.tp3_price else None,
            "tp3_allocation": float(s.tp3_allocation) if s.tp3_allocation else None,
            "stop_loss": float(s.stop_loss) if s.stop_loss else None,
            "alert_enabled": s.alert_enabled,
            "current_price": current_price,
            "avg_cost": avg_cost
        })
    
    return result


@router.post("/exit", response_model=ExitStrategyResponse, status_code=status.HTTP_201_CREATED)
def create_exit_strategy(
    strategy: ExitStrategyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an exit strategy for a holding"""
    portfolio = get_user_portfolio(current_user.id, db)
    
    # Verify holding belongs to user
    holding = db.query(Holding).filter(
        Holding.id == strategy.holding_id,
        Holding.portfolio_id == portfolio.id
    ).first()
    
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holding not found"
        )
    
    # Check if exit strategy already exists
    existing = db.query(ExitStrategy).filter(
        ExitStrategy.holding_id == strategy.holding_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exit strategy already exists for this holding. Use PUT to update."
        )
    
    new_strategy = ExitStrategy(
        holding_id=strategy.holding_id,
        symbol=holding.symbol,
        tp1_price=strategy.tp1_price,
        tp1_allocation=strategy.tp1_allocation,
        tp2_price=strategy.tp2_price,
        tp2_allocation=strategy.tp2_allocation,
        tp3_price=strategy.tp3_price,
        tp3_allocation=strategy.tp3_allocation,
        stop_loss=strategy.stop_loss,
        alert_enabled=strategy.alert_enabled
    )
    
    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)
    
    # Get current price
    current_price = None
    price_data = stock_service.get_stock_price(holding.symbol)
    if price_data:
        current_price = price_data.get('price')
    
    return {
        "id": new_strategy.id,
        "holding_id": new_strategy.holding_id,
        "symbol": new_strategy.symbol,
        "tp1_price": float(new_strategy.tp1_price) if new_strategy.tp1_price else None,
        "tp1_allocation": float(new_strategy.tp1_allocation) if new_strategy.tp1_allocation else None,
        "tp2_price": float(new_strategy.tp2_price) if new_strategy.tp2_price else None,
        "tp2_allocation": float(new_strategy.tp2_allocation) if new_strategy.tp2_allocation else None,
        "tp3_price": float(new_strategy.tp3_price) if new_strategy.tp3_price else None,
        "tp3_allocation": float(new_strategy.tp3_allocation) if new_strategy.tp3_allocation else None,
        "stop_loss": float(new_strategy.stop_loss) if new_strategy.stop_loss else None,
        "alert_enabled": new_strategy.alert_enabled,
        "current_price": current_price,
        "avg_cost": float(holding.avg_cost)
    }


@router.put("/exit/{strategy_id}", response_model=ExitStrategyResponse)
def update_exit_strategy(
    strategy_id: int,
    strategy: ExitStrategyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an exit strategy"""
    portfolio = get_user_portfolio(current_user.id, db)
    
    # Get holdings for this portfolio
    holdings = db.query(Holding).filter(
        Holding.portfolio_id == portfolio.id
    ).all()
    holding_ids = [h.id for h in holdings]
    
    existing = db.query(ExitStrategy).filter(
        ExitStrategy.id == strategy_id,
        ExitStrategy.holding_id.in_(holding_ids)
    ).first()
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exit strategy not found"
        )
    
    # Update fields
    if strategy.tp1_price is not None:
        existing.tp1_price = strategy.tp1_price
    if strategy.tp1_allocation is not None:
        existing.tp1_allocation = strategy.tp1_allocation
    if strategy.tp2_price is not None:
        existing.tp2_price = strategy.tp2_price
    if strategy.tp2_allocation is not None:
        existing.tp2_allocation = strategy.tp2_allocation
    if strategy.tp3_price is not None:
        existing.tp3_price = strategy.tp3_price
    if strategy.tp3_allocation is not None:
        existing.tp3_allocation = strategy.tp3_allocation
    if strategy.stop_loss is not None:
        existing.stop_loss = strategy.stop_loss
    existing.alert_enabled = strategy.alert_enabled
    
    db.commit()
    db.refresh(existing)
    
    # Get holding for avg cost
    holding = db.query(Holding).filter(Holding.id == existing.holding_id).first()
    
    # Get current price
    current_price = None
    price_data = stock_service.get_stock_price(existing.symbol)
    if price_data:
        current_price = price_data.get('price')
    
    return {
        "id": existing.id,
        "holding_id": existing.holding_id,
        "symbol": existing.symbol,
        "tp1_price": float(existing.tp1_price) if existing.tp1_price else None,
        "tp1_allocation": float(existing.tp1_allocation) if existing.tp1_allocation else None,
        "tp2_price": float(existing.tp2_price) if existing.tp2_price else None,
        "tp2_allocation": float(existing.tp2_allocation) if existing.tp2_allocation else None,
        "tp3_price": float(existing.tp3_price) if existing.tp3_price else None,
        "tp3_allocation": float(existing.tp3_allocation) if existing.tp3_allocation else None,
        "stop_loss": float(existing.stop_loss) if existing.stop_loss else None,
        "alert_enabled": existing.alert_enabled,
        "current_price": current_price,
        "avg_cost": float(holding.avg_cost) if holding else None
    }


@router.delete("/exit/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exit_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an exit strategy"""
    portfolio = get_user_portfolio(current_user.id, db)
    
    holdings = db.query(Holding).filter(
        Holding.portfolio_id == portfolio.id
    ).all()
    holding_ids = [h.id for h in holdings]
    
    strategy = db.query(ExitStrategy).filter(
        ExitStrategy.id == strategy_id,
        ExitStrategy.holding_id.in_(holding_ids)
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exit strategy not found"
        )
    
    db.delete(strategy)
    db.commit()
    
    return None


# Strategy Execution Endpoints

@router.post("/entry/{strategy_id}/execute")
def execute_entry_strategy(
    strategy_id: int,
    execution: StrategyExecutionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record an execution of an entry strategy"""
    portfolio = get_user_portfolio(current_user.id, db)
    
    strategy = db.query(EntryStrategy).filter(
        EntryStrategy.id == strategy_id,
        EntryStrategy.portfolio_id == portfolio.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry strategy not found"
        )
    
    amount = execution.shares * execution.price
    
    # Create execution record
    new_execution = StrategyExecution(
        entry_strategy_id=strategy_id,
        execution_type=execution.execution_type.upper(),
        zone_num=execution.zone_num,
        shares=execution.shares,
        price=execution.price,
        amount=amount,
        execution_date=execution.execution_date,
        notes=execution.notes
    )
    
    db.add(new_execution)
    
    # Update deployed capital
    if execution.execution_type.upper() == 'BUY':
        strategy.deployed_capital = (float(strategy.deployed_capital) if strategy.deployed_capital else 0) + amount
    
    # Check if strategy is complete
    if strategy.deployed_capital >= strategy.total_capital:
        strategy.status = 'completed'
    
    db.commit()
    
    return {
        "message": "Execution recorded",
        "execution_id": new_execution.id,
        "deployed_capital": float(strategy.deployed_capital),
        "remaining_capital": float(strategy.total_capital) - float(strategy.deployed_capital)
    }


@router.get("/entry/{strategy_id}/executions")
def get_strategy_executions(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all executions for an entry strategy"""
    portfolio = get_user_portfolio(current_user.id, db)
    
    strategy = db.query(EntryStrategy).filter(
        EntryStrategy.id == strategy_id,
        EntryStrategy.portfolio_id == portfolio.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry strategy not found"
        )
    
    executions = db.query(StrategyExecution).filter(
        StrategyExecution.entry_strategy_id == strategy_id
    ).order_by(StrategyExecution.execution_date.desc()).all()
    
    return [{
        "id": e.id,
        "execution_type": e.execution_type,
        "zone_num": e.zone_num,
        "shares": e.shares,
        "price": float(e.price),
        "amount": float(e.amount),
        "execution_date": e.execution_date.isoformat() if e.execution_date else None,
        "notes": e.notes
    } for e in executions]
