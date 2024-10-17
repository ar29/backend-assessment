from datetime import datetime
from assessment_app.utils.utils import compute_cagr, datetime_to_str, str_to_datetime

# Test for compute_cagr function
def test_compute_cagr():
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 1, 1)
    
    beginning_value = 1000
    ending_value = 2000
    
    expected_cagr = 25.99  # Calculated value for the given inputs
    
    result = compute_cagr(beginning_value, ending_value, start_date, end_date)
    
    assert round(result, 2) == expected_cagr, f"Expected {expected_cagr}, got {result}"

# Test for datetime_to_str function
def test_datetime_to_str():
    dt = datetime(2023, 9, 14)
    expected_str = '2023-09-14'
    
    result = datetime_to_str(dt)
    
    assert result == expected_str, f"Expected {expected_str}, got {result}"

# Test for str_to_datetime function
def test_str_to_datetime():
    date_str = '2023-09-14'
    expected_datetime = datetime(2023, 9, 14)
    
    result = str_to_datetime(date_str)
    
    assert result == expected_datetime, f"Expected {expected_datetime}, got {result}"
