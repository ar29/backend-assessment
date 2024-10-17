import csv
from datetime import datetime
from typing import List

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from assessment_app.models.models import TickData
from assessment_app.models.models import Trade
from assessment_app.models.schema import PortfolioORM, TradeORM, TradeHistoryORM
from assessment_app.service.auth_service import get_current_user
from assessment_app.utils.utils import compute_cagr
from assessment_app.repository.database import get_db

router = APIRouter()


# Helper function to read stock data from CSV
def read_stock_data(stock_symbol: str) -> List[dict]:
    file_path = f"assessment_app/data/{stock_symbol}.csv"
    stock_data = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            stock_data.append(row)
    return stock_data


@router.post("/market/data/tick", response_model=TickData)
async def get_market_data_tick(stock_symbol: str, current_ts: datetime, current_user_id: str = Depends(get_current_user)) -> TickData:
    """
    Get data for stocks for a given datetime from `data` folder.
    Please note consider price value in TickData to be average of open and close price column value for the timestamp from the data file.
    """
    stock_data = read_stock_data(stock_symbol)
    print(stock_data)
    for data in stock_data:

        if datetime.strptime(data['Date'], '%Y-%m-%d').date() == current_ts.date():
            price = (float(data['Open']) + float(data['Close'])) / 2
            return TickData(
                stock_symbol=stock_symbol,
                timestamp=current_ts,
                price=price
            )
    raise HTTPException(status_code=404, detail="Data not found for the given date")


@router.post("/market/data/range", response_model=List[TickData])
async def get_market_data_range(stock_symbol: str, from_ts: datetime, to_ts: datetime, current_user_id: str = Depends(get_current_user)) -> List[TickData]:
    """
    Get data for stocks for a given datetime from `data` folder.
    Please note consider price value in TickData to be average of open and close price column value for the timestamp from the data file.
    """
    stock_data = read_stock_data(stock_symbol)
    tick_data_range = []
    for data in stock_data:
        date = datetime.strptime(data['Date'], '%Y-%m-%d').date()
        if from_ts.date() <= date <= to_ts.date():
            price = (float(data['Open']) + float(data['Close'])) / 2
            tick_data_range.append(TickData(
                stock_symbol=stock_symbol,
                timestamp=date,
                price=price
            ))
    if not tick_data_range:
        raise HTTPException(status_code=404, detail="No data found for the given range")
    return tick_data_range


@router.post("/market/trade", response_model=Trade)
async def trade_stock(trade: Trade, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user)) -> Trade:
    """
    Only if trade.price is within Open and Close price of that stock on the execution timestamp, then trade should be successful.
    Trade.price must be average of Open and Close price of that stock on the execution timestamp.
    Also, update the portfolio and trade history with the trade details and adjust cash and networth appropriately.
    On every trade, current_ts of portfolio also becomes today.
    One cannot place trade in date (Trade.execution_ts) older than portfolio.current_ts
    """
    # Fetch user's portfolio
    portfolio = db.query(PortfolioORM).filter(PortfolioORM.user_id == current_user_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Check if trade date is valid
    if trade.execution_ts.date() < portfolio.current_ts.date():
        raise HTTPException(status_code=400, detail="Cannot trade in the past")

    # Load stock data from CSV
    stock_data_path = f"assessment_app/data/{trade.symbol}.csv"
    try:
        stock_df = pd.read_csv(stock_data_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Stock data not found")

    # Calculate average price
    stock_df['Date'] = pd.to_datetime(stock_df['Date']).dt.date
    trade_data = stock_df[stock_df['Date'] == trade.execution_ts.date()]

    if trade_data.empty:
        raise HTTPException(status_code=404, detail="Trade date not found in stock data")

    avg_price = (trade_data['Open'].values[0] + trade_data['Close'].values[0]) / 2

    # Validate trade price
    if not (trade.price >= trade_data['Open'].values[0] and trade.price <= trade_data['Close'].values[0]):
        print(trade_data['Close'].values[0])
        print(trade_data['Open'].values[0])
        raise HTTPException(status_code=400, detail="Trade price not within the range of open and close prices")

    # Update portfolio cash
    if trade.type == "BUY":
        if portfolio.cash_remaining < trade.price * trade.quantity:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        portfolio.cash_remaining -= trade.price * trade.quantity
    elif trade.type == "SELL":
        portfolio.cash_remaining += trade.price * trade.quantity
    else:
        raise HTTPException(status_code=400, detail="Invalid trade type")

    # Create trade record
    trade_record = TradeORM(
        symbol=trade.symbol,
        price=float(avg_price),
        quantity=trade.quantity,
        trade_type=trade.type,
        execution_ts=trade.execution_ts,
        portfolio_id=portfolio.id
    )
    import pytz
    # Create trade history record
    trade_history = TradeHistoryORM(
        portfolio_id=portfolio.id,
        date=datetime.now(pytz.timezone('Asia/Kolkata'))
    )
    
    
    db.add(trade_history)
    db.commit()
    trade_record.history_id = trade_history.id
    db.add(trade_record)
    db.commit()
    db.refresh(trade_record)
    db.refresh(trade_history)

    import pytz
    # Update portfolio timestamp
    portfolio.current_ts = datetime.now(pytz.timezone('Asia/Kolkata'))
    db.commit()
    db.refresh(portfolio)

    return trade_record
