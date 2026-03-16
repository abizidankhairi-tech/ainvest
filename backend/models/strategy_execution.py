from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Numeric, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class StrategyExecution(Base):
    __tablename__ = "strategy_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    entry_strategy_id = Column(Integer, ForeignKey("entry_strategies.id", ondelete="CASCADE"), nullable=False)
    execution_type = Column(String(10), nullable=False)  # BUY, SELL
    zone_num = Column(Integer)
    shares = Column(Integer, nullable=False)
    price = Column(Numeric(15, 2), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    execution_date = Column(Date, nullable=False)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    entry_strategy = relationship("EntryStrategy", back_populates="executions")
