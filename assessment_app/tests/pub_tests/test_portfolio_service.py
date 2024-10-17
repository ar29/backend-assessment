from unittest.mock import MagicMock
from datetime import datetime
from assessment_app.routers.analysis import get_portfolio_for_user
from assessment_app.models.models import Portfolio, Holding
import pytest
from fastapi import HTTPException

def test_get_portfolio_for_user():
    # Mock the DB session and query results
    mock_db = MagicMock()

    import pytz
    mock_portfolio = Portfolio(id="1", cash_remaining=1000000.0, current_ts=datetime.now(pytz.timezone('Asia/Kolkata')), holdings=[])
    mock_portfolio.holdings = [
        Holding(symbol="HDFCBANK", quantity=100, price=100),
        Holding(symbol="RELIANCE", quantity=50, price=100),
    ]
    
    mock_db.query.return_value.filter.return_value.first.return_value = mock_portfolio

    portfolio = get_portfolio_for_user("test_user", mock_db)
    
    # assert portfolio.user_id == "test_user"
    assert len(portfolio.holdings) == 2
    assert portfolio.holdings[0].symbol == "HDFCBANK"

def test_get_portfolio_for_user_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_portfolio_for_user("invalid_user", mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Portfolio not found for the user"
