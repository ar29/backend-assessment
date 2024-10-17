import datetime

from assessment_app.models.constants import DAYS_IN_YEAR
from datetime import datetime


def compute_cagr(beginning_value: float, ending_value: float, start_date: datetime, end_date: datetime) -> float:
    """
    Compute the Compound Annual Growth Rate (CAGR).

    Parameters:
    beginning_value (float): The initial value of the investment.
    ending_value (float): The value of the investment at the end of the period.
    start_date (datetime): The starting date of the investment.
    end_date (datetime): The ending date of the investment.

    Returns:
    float: The CAGR as a decimal.

    Example:
        12% CAGR for the specified duration would return 12.0 as output from this method
        200% CAGR would mean your returned value would be 200 for the duration
        5% CAGR would mean your returned value would be 5 for the duration
    """
    # Calculate the number of days between start_date and end_date
    duration_in_days = (end_date - start_date).days
    
    # Calculate the number of years between the two dates
    duration_in_years = duration_in_days / DAYS_IN_YEAR

    # Calculate CAGR using the formula
    if duration_in_years == 0 or beginning_value == 0:
        return 0.0
    cagr = ((ending_value / beginning_value) ** (1 / duration_in_years) - 1) * 100
    return cagr


def datetime_to_str(dt: datetime) -> str:
    """
    Convert a datetime object to a string in the format 'YYYY-MM-DD'.

    Parameters:
    dt (datetime): The datetime object to convert.

    Returns:
    str: The datetime as a string.
    """
    return dt.strftime('%Y-%m-%d')


def str_to_datetime(date_str: str) -> datetime:
    """
    Convert a string in the format 'YYYY-MM-DD' to a datetime object.

    Parameters:
    date_str (str): The string to convert.

    Returns:
    datetime: The datetime object.
    """
    return datetime.strptime(date_str, '%Y-%m-%d')
