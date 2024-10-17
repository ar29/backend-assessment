from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from assessment_app.models.models import Portfolio, Holding, PortfolioRequest, Strategy
from assessment_app.models.schema import PortfolioORM, HoldingORM
from assessment_app.repository.database import get_db
from assessment_app.service.auth_service import get_current_user

router = APIRouter()


@router.get("/strategies", response_model=List[Strategy])
async def get_strategies(current_user_id: str = Depends(get_current_user)) -> List[Strategy]:
    """
    Get all strategies available. You do not need to implement this.
    """
    return [
        Strategy(
            id="0",
            name="default"
        )
    ]


@router.post("/portfolio", response_model=Portfolio)
async def create_portfolio(portfolio_request: PortfolioRequest, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user)) -> Portfolio:
    """
    Create a new portfolio and initialise with funds with empty holdings.
    """
    import pytz
    portfolio = PortfolioORM(
        user_id=current_user_id,
        strategy_id=portfolio_request.strategy_id,
        cash_remaining=portfolio_request.cash_remaining or 1000000.0,
        current_ts=datetime.now(pytz.timezone('Asia/Kolkata')),
    )
    db.add(portfolio)
    db.commit()

    holdings_response = []
    # Add holdings if any are provided
    for holding_data in portfolio_request.holdings:
        holding = HoldingORM(
            portfolio_id=portfolio.id,
            symbol=holding_data.symbol,
            quantity=holding_data.quantity,
            price=holding_data.price
        )
        db.add(holding)
        holdings_response.append(Holding(symbol=holding.symbol, quantity=holding.quantity, price=holding.price))

    db.commit()
    db.refresh(portfolio)
    portfolio_response = Portfolio(id=portfolio.id, cash_remaining=portfolio.cash_remaining, current_ts=portfolio.current_ts, holdings=holdings_response)
    return portfolio_response


@router.get("/portfolio/{portfolio_id}", response_model=Portfolio)
async def get_portfolio_by_id(portfolio_id: str, current_ts: datetime, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user)) -> Portfolio:
    """
    Get specified portfolio for the current user.
    """
    portfolio = db.query(PortfolioORM).filter(PortfolioORM.id == portfolio_id, PortfolioORM.user_id == current_user_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    holdings_response = []
    for holding in portfolio.holdings:
        holdings_response.append(Holding(symbol=holding.symbol, quantity=holding.quantity, price=holding.price))
    portfolio_response = Portfolio(id=portfolio.id, cash_remaining=portfolio.cash_remaining, current_ts=portfolio.current_ts, holdings=holdings_response)
    return portfolio_response


@router.delete("/portfolio/{portfolio_id}", response_model=Portfolio)
async def delete_portfolio(portfolio_id: str, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user)) -> Portfolio:
    """
    Delete the specified portfolio for the current user.
    """
    portfolio = db.query(PortfolioORM).filter(PortfolioORM.id == portfolio_id, PortfolioORM.user_id == current_user_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    holdings_response = []
    for holding in portfolio.holdings:
        holdings_response.append(Holding(symbol=holding.symbol, quantity=holding.quantity, price=holding.price))
    
    db.delete(portfolio)
    db.commit()
    portfolio_response = Portfolio(id=portfolio.id, cash_remaining=portfolio.cash_remaining, current_ts=portfolio.current_ts, holdings=holdings_response)
    return portfolio_response


@router.get("/portfolio-net-worth", response_model=float)
async def get_net_worth(portfolio_id: str, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user)) -> float:
    """
    Get net-worth from portfolio (holdings value and cash) at current_ts field in portfolio.
    """
    portfolio = db.query(PortfolioORM).filter(PortfolioORM.id == portfolio_id, PortfolioORM.user_id == current_user_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    holdings_value = sum([holding.quantity * holding.price for holding in portfolio.holdings])
    net_worth = holdings_value + portfolio.cash_remaining
    return net_worth
