from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Numeric, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    holding_id = Column(Integer, ForeignKey("holdings.id", ondelete="SET NULL"))
    transaction_type = Column(String(10), nullable=False)  # BUY, SELL
    symbol = Column(String(10), nullable=False)
    shares = Column(Integer, nullable=False)
    price = Column(Numeric(15, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    fees = Column(Numeric(15, 2), default=0)
    transaction_date = Column(Date, nullable=False)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
    holding = relationship("Holding", back_populates="transactions")
