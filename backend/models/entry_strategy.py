from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class EntryStrategy(Base):
    __tablename__ = "entry_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(10), nullable=False)
    buy_zones = Column(JSON, nullable=False)  # [{"zone_num": 1, "min_price": 56, "max_price": 58, "allocation": 40}]
    total_capital = Column(Numeric(15, 2), nullable=False)
    deployed_capital = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='active')  # active, completed, cancelled
    alert_enabled = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="entry_strategies")
    executions = relationship("StrategyExecution", back_populates="entry_strategy", cascade="all, delete-orphan")
