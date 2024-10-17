import uuid
from datetime import datetime
from typing import List
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from assessment_app.repository.database import Base


class UserORM(Base):
    __tablename__ = "users"
    
    email = Column(String, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    
    class Config:
        orm_mode = True


class UserCredentialsORM(Base):
    __tablename__= "user_credentials"
    __allow_unmapped__ = True
    

    email = Column(String, primary_key=True)
    password_hash = Column(String)
    random_salt = Column(String)

    class Config:
        orm_mode = True


class PortfolioORM(Base):
    __tablename__ = "portfolios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('user_credentials.email'))
    strategy_id = Column(String)
    cash_remaining = Column(Float, default=1000000.0)
    import pytz
    current_ts = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Kolkata')))

    user = relationship("UserCredentialsORM", backref="portfolios")
    
    # Portfolio can have many holdings
    holdings = relationship("HoldingORM", backref="portfolios", cascade="all, delete-orphan")

    trades = relationship("TradeORM", backref="portfolios", cascade="all, delete-orphan")
    trade_histories = relationship("TradeHistoryORM", backref="portfolios", cascade="all, delete-orphan")

    class Config:
        orm_mode = True

# Assuming Holding model should also be linked
class HoldingORM(Base):
    __tablename__ = "holdings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String, ForeignKey("portfolios.id"))
    symbol = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    
    portfolio = relationship("PortfolioORM", back_populates="holdings")

    class Config:
        orm_mode = True


class TradeORM(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    trade_type = Column(String, nullable=False)  # 'BUY' or 'SELL'
    execution_ts = Column(DateTime, nullable=False)
    portfolio_id = Column(String, ForeignKey('portfolios.id'), nullable=False)
    history_id = Column(Integer, ForeignKey('trade_histories.id'))
    
    portfolio = relationship("PortfolioORM", back_populates="trades")



class TradeHistoryORM(Base):
    __tablename__ = "trade_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(String, ForeignKey('portfolios.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    
    portfolio = relationship("PortfolioORM", back_populates="trade_histories")
    # One-to-many relationship with trades
    trades = relationship('TradeORM', backref='trade_history', cascade="all, delete-orphan")