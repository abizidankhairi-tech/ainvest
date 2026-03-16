from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(10))
    recommendation = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Numeric(3, 2))  # 0.0 to 1.0
    reasoning = Column(Text, nullable=False)
    target_price = Column(Numeric(15, 2))
    stop_loss = Column(Numeric(15, 2))
    time_horizon = Column(String(20))  # short, medium, long
    status = Column(String(20), default='active')  # active, executed, expired
    expires_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="ai_recommendations")
