import csv
from datetime import datetime

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from assessment_app.models.constants import StockSymbols
from assessment_app.service.auth_service import get_current_user
from assessment_app.utils.utils import compute_cagr, datetime_to_str
from assessment_app.repository.database import get_db
from assessment_app.service.portfolio_service import get_portfolio_for_user


router = APIRouter()



def get_stock_data(stock_symbol: str):
    file_path = f'assessment_app/data/{stock_symbol}.csv'
    stock_data = []
    
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                stock_data.append({
                    "date": datetime.strptime(row["Date"], "%Y-%m-%d"),
                    "close": float(row["Close"]),
                })
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Stock data not found")
    
    return stock_data


@router.get("/analysis/estimate_returns/stock", response_model=float)
async def get_stock_analysis(stock_symbol: str, start_ts: datetime, end_ts: datetime, current_user_id: str = Depends(get_current_user)) -> float:
    """
    Estimate returns for given stock based on stock prices between the given timestamps.
    Use compute_cagr method
    Example:
        200% CAGR would mean your returned value would be 200 for the duration
        5% CAGR would mean your returned value would be 5 for the duration
    """
    stock_data = get_stock_data(stock_symbol)
    
    # Get starting and ending prices based on start and end timestamps
    for data in stock_data:
        if data["date"].date() == start_ts.date():
            start_price = data["close"]
        if data["date"].date() == end_ts.date():
            end_price = data["close"]

    if start_price is None or end_price is None:
        raise HTTPException(status_code=400, detail="Invalid start or end date")
    
    # Calculate CAGR
    cagr = compute_cagr(start_price, end_price, start_ts, end_ts)
    return cagr


@router.get("/analysis/estimate_returns/portfolio")
async def estimate_portfolio_returns(start_ts: datetime, end_ts: datetime, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Estimate returns for the current portfolio based on stock prices between the given timestamps.
    Use compute_cagr method.
    Example:
        100% CAGR would mean your returned value would be 2.0 for the duration
        5% CAGR would mean your returned value would be 1.05 for the duration
    """

    portfolio = get_portfolio_for_user(current_user_id, db)
    total_start_value = 0
    total_end_value = 0

    for holding in portfolio.holdings:
        stock_data = get_stock_data(holding.symbol)
        start_price = next((data["close"] for data in stock_data if data["date"].date() == start_ts.date()), None)
        end_price = next((data["close"] for data in stock_data if data["date"].date() == end_ts.date()), None)
        
        if start_price is None or end_price is None:
            raise HTTPException(status_code=400, detail="Invalid start or end date for stock")

        # Calculate the total value of the portfolio based on stock holdings
        total_start_value += holding.quantity * start_price
        total_end_value += holding.quantity * end_price

    if total_start_value == 0:
        raise HTTPException(status_code=400, detail="Portfolio has no value at the start")

    cagr = compute_cagr(total_start_value, total_end_value, start_ts, end_ts)
    return cagr
