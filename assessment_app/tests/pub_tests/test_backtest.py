# import pytest
# from fastapi.testclient import TestClient
# from datetime import datetime
# from assessment_app.main import app
# import pandas as pd
# from assessment_app.models.schema import BacktestRequest, BacktestResponse

# client = TestClient(app)

# @pytest.fixture
# def setup_data():
#     # Prepare stock data for testing
#     df = pd.DataFrame({
#         'Date': ['2023-07-19', '2023-07-20', '2023-07-21'],
#         'Open': [614.0, 622.65, 621.0],
#         'Close': [620.6, 621.65, 625.75]
#     })
#     df.to_csv('assessment_app/data/TATAMOTORS.csv', index=False)

# def test_backtest_strategy():
#     # Prepare a mock request
#     backtest_request = {
#         "strategy_id": "1",
#         "portfolio_id": "1",
#         "start_date": "2023-07-19",
#         "end_date": "2023-07-21",
#         "initial_capital": 100000.0
#     }

#     response = client.post("/backtest", json=backtest_request)
#     assert response.status_code == 200

#     data = response.json()
#     assert data["start_date"] == "2023-07-19"
#     assert data["end_date"] == "2023-07-21"
#     assert data["initial_capital"] == 100000.0
#     assert "final_capital" in data
#     assert "trades" in data
#     assert data["profit_loss"] == data["final_capital"] - data["initial_capital"]
#     assert "annualized_return" in data