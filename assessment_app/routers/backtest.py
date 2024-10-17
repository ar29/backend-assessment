from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends
import pandas as pd
from sqlalchemy.orm import Session

from assessment_app.models.models import BacktestRequest, BacktestResponse, Trade
from assessment_app.models.schema import PortfolioORM
from assessment_app.service.auth_service import get_current_user
from assessment_app.utils.utils import compute_cagr
from assessment_app.repository.database import get_db

router = APIRouter()

@router.post("/backtest", response_model=BacktestResponse)
async def backtest_strategy(
    request: BacktestRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
) -> BacktestResponse:
    """
    Backtest a trading strategy over a specified period, buying/selling stocks
    based on holdings in the given portfolio.
    """
    
    # Load portfolio from the database
    portfolio = db.query(PortfolioORM).filter(PortfolioORM.id == request.portfolio_id, PortfolioORM.user_id == current_user_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Load portfolio holdings
    holdings = portfolio.holdings
    if not holdings:
        raise HTTPException(status_code=404, detail="No holdings found for the portfolio")

    # Load stock data
    stock_data_files = {
        'HDFCBANK': 'assessment_app/data/HDFCBANK.csv',
        'ICICIBANK': 'assessment_app/data/ICICIBANK.csv',
        'RELIANCE': 'assessment_app/data/RELIANCE.csv',
        'TATAMOTORS': 'assessment_app/data/TATAMOTORS.csv'
    }

    # Initialize backtest variables
    capital = request.initial_capital
    trades = []
    
    for holding in holdings:
        stock_symbol = holding.symbol
        if stock_symbol not in stock_data_files:
            continue
        
        file_path = stock_data_files[stock_symbol]
        try:
            df = pd.read_csv(file_path)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        except FileNotFoundError:
            continue

        # Filter data for the backtest period
        df = df[(df['Date'] >= request.start_date.date()) & (df['Date'] <= request.end_date.date())]
        
        if df.empty:
            continue

        # Simulate trading based on the strategy (mock implementation)
        for index, row in df.iterrows():
            if capital <= 0:
                break

            # Example trade logic
            if row['Close'] < row['Open']:
                # Assume we buy 100 units of stock when price is lower
                quantity = 100
                cost = quantity * row['Close']
                if capital >= cost:
                    capital -= cost
                    # Update holdings for the portfolio
                    holding.quantity += quantity
                    trades.append(Trade(
                        symbol=stock_symbol,
                        price=row['Close'],
                        quantity=quantity,
                        type='BUY',
                        execution_ts=row['Date']
                    ))
            
            elif row['Close'] > row['Open'] and holding.quantity >= 100:
                # Assume we sell 100 units of stock when price is higher
                quantity = 100
                revenue = quantity * row['Close']
                capital += revenue
                # Update holdings for the portfolio
                holding.quantity -= quantity
                trades.append(Trade(
                    symbol=stock_symbol,
                    price=row['Close'],
                    quantity=quantity,
                    type='SELL',
                    execution_ts=row['Date']
                ))

    # Update the portfolio's cash remaining
    portfolio.cash_remaining = capital
    db.commit()

    # Calculate profit/loss as final capital minus initial capital
    final_capital = capital
    profit_loss = final_capital - request.initial_capital

    # Calculate annualized return
    end_date = request.end_date
    start_date = request.start_date
    annualized_return = compute_cagr(request.initial_capital, final_capital, start_date, end_date)

    return BacktestResponse(
        start_date=start_date,
        end_date=end_date,
        initial_capital=request.initial_capital,
        final_capital=final_capital,
        trades=trades,
        profit_loss=profit_loss,
        annualized_return=annualized_return
    )
