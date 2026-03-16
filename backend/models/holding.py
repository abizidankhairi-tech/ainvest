from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Holding(Base):
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(10), nullable=False)
    shares = Column(Integer, nullable=False)
    avg_cost = Column(Numeric(15, 2), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('portfolio_id', 'symbol', name='unique_portfolio_symbol'),
    )
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    transactions = relationship("Transaction", back_populates="holding")
    exit_strategy = relationship("ExitStrategy", back_populates="holding", uselist=False)
