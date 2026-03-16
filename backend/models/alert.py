from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Numeric, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # price_target, stop_loss, rebalance, dividend, news
    symbol = Column(String(10))
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"))
    trigger_price = Column(Numeric(15, 2))
    trigger_condition = Column(String(20))  # above, below
    message = Column(Text, nullable=False)
    status = Column(String(20), default='active')  # active, triggered, expired
    channels = Column(JSON, default=['in-app'])  # ["in-app", "email", "sms"]
    triggered_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    portfolio = relationship("Portfolio", back_populates="alerts")
