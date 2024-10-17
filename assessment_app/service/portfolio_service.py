from sqlalchemy.orm import Session
from fastapi import HTTPException
from assessment_app.models.schema import PortfolioORM
from assessment_app.models.models import Portfolio, Holding

def get_portfolio_for_user(user_id: str, db: Session) -> Portfolio:
    """
    Retrieve the portfolio of the current user from the database.

    Parameters:
    - user_id: str : The ID of the current user.
    - db: Session : The database session.

    Returns:
    - Portfolio: The user's portfolio if it exists.
    """
    portfolio = db.query(PortfolioORM).filter(PortfolioORM.user_id == user_id).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found for the user")
    
    holdings_response = []
    for holding in portfolio.holdings:
        holdings_response.append(Holding(symbol=holding.symbol, quantity=holding.quantity, price=holding.price))
    portfolio_response = Portfolio(id=portfolio.id, cash_remaining=portfolio.cash_remaining, current_ts=portfolio.current_ts, holdings=holdings_response)
    return portfolio_response
