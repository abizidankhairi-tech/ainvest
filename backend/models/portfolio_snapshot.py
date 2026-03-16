from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, Numeric, Date, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    total_value = Column(Numeric(15, 2), nullable=False)
    total_cost = Column(Numeric(15, 2), nullable=False)
    unrealized_gain = Column(Numeric(15, 2))
    cash_balance = Column(Numeric(15, 2), default=0)
    snapshot_date = Column(Date, nullable=False)
    holdings_snapshot = Column(JSON)  # Complete holdings data
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('portfolio_id', 'snapshot_date', name='unique_portfolio_snapshot_date'),
    )
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="snapshots")
