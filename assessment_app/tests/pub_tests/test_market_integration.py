# import pytest
# from fastapi.testclient import TestClient
# from datetime import datetime
# from assessment_app.main import app
# from assessment_app.models.schema import Portfolio, Trade, TradeHistory
# from sqlalchemy.orm import Session
# import pandas as pd

# client = TestClient(app)

# # Helper function to create a portfolio
# def create_portfolio(db: Session, user_id: str, cash_remaining: float = 1000000.0) -> Portfolio:
#     import pytz
#     portfolio = Portfolio(user_id=user_id, strategy_id="1", cash_remaining=cash_remaining, current_ts=datetime.now(pytz.timezone('Asia/Kolkata')))
#     db.add(portfolio)
#     db.commit()
#     db.refresh(portfolio)
#     return portfolio

# # Test for /market/data/tick endpoint
# def test_get_market_data_tick():
#     stock_symbol = "HDFCBANK"
#     timestamp = datetime(2023, 7, 20)
    
#     response = client.post("/market/data/tick", json={"stock_symbol": stock_symbol, "current_ts": timestamp.isoformat()})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["stock_symbol"] == stock_symbol
#     assert data["timestamp"] == timestamp.isoformat()
#     assert "price" in data

# # Test for /market/data/range endpoint
# def test_get_market_data_range():
#     stock_symbol = "ICICIBANK"
#     from_ts = datetime(2023, 7, 19)
#     to_ts = datetime(2023, 7, 21)
    
#     response = client.post("/market/data/range", json={"stock_symbol": stock_symbol, "from_ts": from_ts.isoformat(), "to_ts": to_ts.isoformat()})
#     assert response.status_code == 200
#     data = response.json()
#     assert isinstance(data, list)
#     assert len(data) > 0
#     assert data[0]["stock_symbol"] == stock_symbol

# # Test for /market/trade endpoint
# @pytest.fixture
# def setup_portfolio_and_user(db: Session):
#     user_id = "testuser@example.com"
#     create_portfolio(db, user_id)
#     return user_id

# # Helper function to create a portfolio
# def create_portfolio(db: Session, user_id: str, cash_remaining: float = 1000000.0) -> Portfolio:
#     import pytz
#     portfolio = Portfolio(id="1", user_id=user_id, strategy_id="1", cash_remaining=cash_remaining, current_ts=datetime.now(pytz.timezone('Asia/Kolkata')))
#     db.add(portfolio)
#     db.commit()
#     db.refresh(portfolio)
#     return portfolio

# # Helper function to add stock data
# def add_stock_data():
#     df = pd.DataFrame({
#         'Date': ['2023-07-19', '2023-07-20', '2023-07-21'],
#         'Open': [614.0, 622.65, 621.0],
#         'Close': [620.6, 621.65, 625.75]
#     })
#     df.to_csv('assessment_app/data/TATAMOTORS.csv', index=False)

# def test_trade_stock(setup_portfolio_and_user, db: Session):
#     add_stock_data()
#     user_id = setup_portfolio_and_user
#     trade = {
#         "symbol": "TATAMOTORS",
#         "price": 620.0,
#         "quantity": 10,
#         "trade_type": "BUY",
#         "execution_ts": datetime(2023, 7, 20).isoformat()
#     }

#     response = client.post("/market/trade", json=trade)

#     assert response.status_code == 200
#     data = response.json()
#     assert data["symbol"] == trade["symbol"]
#     assert data["price"] == trade["price"]
#     assert data["quantity"] == trade["quantity"]
#     assert data["trade_type"] == trade["trade_type"]

#     # Verify trade history and portfolio updates
#     trade_record = db.query(Trade).filter(Trade.symbol == trade["symbol"]).first()
#     assert trade_record is not None
#     assert trade_record.price == (614.0 + 620.6) / 2  # Average price

#     trade_history = db.query(TradeHistory).filter(TradeHistory.portfolio_id == "1").first()
#     assert trade_history is not None
#     import pytz
#     assert trade_history.date.date() == datetime.now(pytz.timezone('Asia/Kolkata')).date()

#     portfolio = db.query(Portfolio).filter(Portfolio.id == "1").first()
#     assert portfolio is not None
#     assert portfolio.cash_remaining == 1000000.0 - (620.0 * 10)
#     assert portfolio.current_ts.date() == datetime.now(pytz.timezone('Asia/Kolkata')).date()