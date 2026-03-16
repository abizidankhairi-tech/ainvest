from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class ExitStrategy(Base):
    __tablename__ = "exit_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    holding_id = Column(Integer, ForeignKey("holdings.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(10), nullable=False)
    tp1_price = Column(Numeric(15, 2))
    tp1_allocation = Column(Numeric(5, 2))
    tp2_price = Column(Numeric(15, 2))
    tp2_allocation = Column(Numeric(5, 2))
    tp3_price = Column(Numeric(15, 2))
    tp3_allocation = Column(Numeric(5, 2))
    stop_loss = Column(Numeric(15, 2))
    alert_enabled = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    holding = relationship("Holding", back_populates="exit_strategy")
