from sqlalchemy import Column, Integer, String, TIMESTAMP, Numeric, BigInteger, Index
from sqlalchemy.sql import func
from database import Base


class StockPrice(Base):
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False)
    price = Column(Numeric(15, 2), nullable=False)
    open = Column(Numeric(15, 2))
    high = Column(Numeric(15, 2))
    low = Column(Numeric(15, 2))
    close = Column(Numeric(15, 2))
    volume = Column(BigInteger)
    change = Column(Numeric(15, 2))
    change_pct = Column(Numeric(10, 4))
    timestamp = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        Index('idx_stock_prices_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_stock_prices_timestamp', 'timestamp'),
    )
