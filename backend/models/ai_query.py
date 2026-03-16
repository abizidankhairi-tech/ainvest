from sqlalchemy import Column, Integer, Boolean, TIMESTAMP, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class AIQuery(Base):
    __tablename__ = "ai_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"))
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    context = Column(JSON)
    satisfied = Column(Boolean)  # User feedback
    tokens_used = Column(Integer)
    response_time_ms = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ai_queries")
    portfolio = relationship("Portfolio", back_populates="ai_queries")
