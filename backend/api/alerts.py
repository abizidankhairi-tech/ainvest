from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import get_db
from models.user import User
from models.portfolio import Portfolio
from models.alert import Alert
from models.notification import Notification
from api.auth import get_current_user
from services.stock_service import stock_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


# Pydantic models
class AlertCreate(BaseModel):
    alert_type: str  # price_target, stop_loss, price_above, price_below
    symbol: str
    trigger_price: float
    trigger_condition: str  # above, below
    message: Optional[str] = None
    channels: List[str] = ["in-app"]  # in-app, email, sms


class AlertResponse(BaseModel):
    id: int
    alert_type: str
    symbol: str
    trigger_price: float
    trigger_condition: str
    message: str
    status: str
    channels: List[str]
    current_price: Optional[float] = None
    distance_pct: Optional[float] = None
    triggered_at: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    action_url: Optional[str]
    is_read: bool
    created_at: Optional[str]
    
    class Config:
        from_attributes = True


def get_user_portfolio(user_id: int, db: Session) -> Portfolio:
    """Get user's active portfolio"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.user_id == user_id,
        Portfolio.is_active == True
    ).first()
    return portfolio


@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all alerts for the user"""
    query = db.query(Alert).filter(Alert.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Alert.status == status_filter)
    
    alerts = query.order_by(Alert.created_at.desc()).all()
    
    # Get current prices for all symbols
    symbols = list(set([a.symbol for a in alerts if a.symbol]))
    prices = stock_service.get_multiple_prices(symbols) if symbols else {}
    
    result = []
    for a in alerts:
        current_price = None
        distance_pct = None
        
        if a.symbol and a.symbol in prices:
            current_price = prices[a.symbol].get('price')
            if current_price and a.trigger_price:
                distance_pct = ((float(a.trigger_price) - current_price) / current_price) * 100
        
        result.append({
            "id": a.id,
            "alert_type": a.alert_type,
            "symbol": a.symbol,
            "trigger_price": float(a.trigger_price) if a.trigger_price else 0,
            "trigger_condition": a.trigger_condition,
            "message": a.message,
            "status": a.status,
            "channels": a.channels if a.channels else ["in-app"],
            "current_price": current_price,
            "distance_pct": round(distance_pct, 2) if distance_pct else None,
            "triggered_at": a.triggered_at.isoformat() if a.triggered_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else None
        })
    
    return result


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new price alert"""
    portfolio = get_user_portfolio(current_user.id, db)
    
    # Validate alert type
    valid_types = ['price_target', 'stop_loss', 'price_above', 'price_below']
    if alert.alert_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid alert type. Use one of: {', '.join(valid_types)}"
        )
    
    # Validate trigger condition
    if alert.trigger_condition not in ['above', 'below']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trigger condition must be 'above' or 'below'"
        )
    
    # Generate message if not provided
    message = alert.message
    if not message:
        action = "rises above" if alert.trigger_condition == 'above' else "falls below"
        message = f"{alert.symbol.upper()} {action} Rp {alert.trigger_price:,.0f}"
    
    new_alert = Alert(
        user_id=current_user.id,
        portfolio_id=portfolio.id if portfolio else None,
        alert_type=alert.alert_type,
        symbol=alert.symbol.upper(),
        trigger_price=alert.trigger_price,
        trigger_condition=alert.trigger_condition,
        message=message,
        status='active',
        channels=alert.channels
    )
    
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    
    # Get current price
    current_price = None
    distance_pct = None
    price_data = stock_service.get_stock_price(alert.symbol)
    if price_data:
        current_price = price_data.get('price')
        if current_price:
            distance_pct = ((alert.trigger_price - current_price) / current_price) * 100
    
    return {
        "id": new_alert.id,
        "alert_type": new_alert.alert_type,
        "symbol": new_alert.symbol,
        "trigger_price": float(new_alert.trigger_price),
        "trigger_condition": new_alert.trigger_condition,
        "message": new_alert.message,
        "status": new_alert.status,
        "channels": new_alert.channels,
        "current_price": current_price,
        "distance_pct": round(distance_pct, 2) if distance_pct else None,
        "triggered_at": None,
        "created_at": new_alert.created_at.isoformat() if new_alert.created_at else None
    }


@router.put("/{alert_id}")
def update_alert(
    alert_id: int,
    trigger_price: Optional[float] = None,
    status_update: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    if trigger_price is not None:
        alert.trigger_price = trigger_price
        # Update message
        action = "rises above" if alert.trigger_condition == 'above' else "falls below"
        alert.message = f"{alert.symbol} {action} Rp {trigger_price:,.0f}"
    
    if status_update:
        if status_update not in ['active', 'triggered', 'expired', 'cancelled']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status"
            )
        alert.status = status_update
        if status_update == 'triggered':
            alert.triggered_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Alert updated successfully"}


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return None


@router.post("/check")
def check_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check all active alerts against current prices and trigger if conditions met"""
    active_alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.status == 'active'
    ).all()
    
    if not active_alerts:
        return {"triggered": [], "checked": 0}
    
    # Get current prices
    symbols = list(set([a.symbol for a in active_alerts]))
    prices = stock_service.get_multiple_prices(symbols)
    
    triggered_alerts = []
    
    for alert in active_alerts:
        if alert.symbol not in prices:
            continue
        
        current_price = prices[alert.symbol].get('price')
        if not current_price:
            continue
        
        trigger_price = float(alert.trigger_price)
        should_trigger = False
        
        if alert.trigger_condition == 'above' and current_price >= trigger_price:
            should_trigger = True
        elif alert.trigger_condition == 'below' and current_price <= trigger_price:
            should_trigger = True
        
        if should_trigger:
            # Update alert status
            alert.status = 'triggered'
            alert.triggered_at = datetime.utcnow()
            
            # Create notification
            notification = Notification(
                user_id=current_user.id,
                type='alert',
                title=f"Price Alert: {alert.symbol}",
                message=f"{alert.message}. Current price: Rp {current_price:,.0f}",
                action_url=f"/portfolio?symbol={alert.symbol}",
                is_read=False
            )
            db.add(notification)
            
            triggered_alerts.append({
                "id": alert.id,
                "symbol": alert.symbol,
                "trigger_price": trigger_price,
                "current_price": current_price,
                "message": alert.message
            })
    
    db.commit()
    
    return {
        "triggered": triggered_alerts,
        "checked": len(active_alerts)
    }


# Notifications endpoints

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(
    unread_only: bool = False,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(
        Notification.created_at.desc()
    ).limit(limit).all()
    
    return [{
        "id": n.id,
        "type": n.type,
        "title": n.title,
        "message": n.message,
        "action_url": n.action_url,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat() if n.created_at else None
    } for n in notifications]


@router.get("/notifications/count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {"unread_count": count}


@router.put("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    db.commit()
    
    return {"message": "Notification marked as read"}


@router.put("/notifications/read-all")
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {"message": "All notifications marked as read"}
