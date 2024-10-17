# import pytest
# from fastapi.testclient import TestClient
# from unittest.mock import patch
# from assessment_app.main import app
# from datetime import datetime

# client = TestClient(app)

# @pytest.fixture
# def mock_stock_data():
#     return [
#         {"date": datetime(2023, 7, 19), "close": 620.6},
#         {"date": datetime(2023, 7, 20), "close": 621.65},
#         {"date": datetime(2023, 7, 21), "close": 625.75},
#     ]

# @patch("assessment_app.routers.analysis.get_stock_data")
# def test_get_stock_analysis(mock_get_stock_data, mock_stock_data):
#     mock_get_stock_data.return_value = mock_stock_data

#     response = client.get(
#         "/analysis/estimate_returns/stock?stock_symbol=HDFCBANK&start_ts=2023-07-19T00:00:00&end_ts=2023-07-21T00:00:00"
#     )
#     assert response.status_code == 200
#     assert response.json() == pytest.approx(0.414, 0.001)  # Mock CAGR value


# @patch("assessment_app.routers.analysis.get_portfolio_for_user")
# @patch("assessment_app.routers.analysis.get_stock_data")
# def test_estimate_portfolio_returns(mock_get_stock_data, mock_get_portfolio, mock_stock_data):
#     mock_get_stock_data.return_value = mock_stock_data
#     mock_get_portfolio.return_value = {
#         "holdings": [
#             {"symbol": "HDFCBANK", "quantity": 100},
#             {"symbol": "RELIANCE", "quantity": 50},
#         ]
#     }

#     response = client.get(
#         "/analysis/estimate_returns/portfolio?start_ts=2023-07-19T00:00:00&end_ts=2023-07-21T00:00:00"
#     )
#     assert response.status_code == 200
#     assert response.json() == pytest.approx(0.42, 0.001)  # Mock CAGR value
