"""
Fixed income analytics for bonds

Implements various functions useful for bond analytics.
"""


import datetime
import dateutil.relativedelta
import numpy as np


from .utils import MONTHS_IN_YEAR
from .utils import day_count_factor


def accrint(issue : datetime.date, first_interest : datetime.date, settlement : datetime.date, rate : float, par : float, frequency : int, basis : int = 0) -> float:
    """
    Returns the accrued interest for a bond.

    Parameters
    ----------
    issue : datetime.date
        The bond's issue date.
    first_interest : datetime.date
        The bonds's first coupon date.
    settlement : datetime.date
        The bond's settlement date.
    rate : float
        The bond's annual coupon rate.
    par : float
        The bond's par value.
    frequency : int
        The number of coupon payments per year.
    basis : int [optional]
        The type of day count basis to use.
            - 0 [default] : US (NASD) 30/360
            - 1 : Actual/Actual
            - 2 : Actual/360
            - 3 : Actual/365
            - 4 : European 30/360

    Returns
    -------
    float
        The accrued interest of the bond.
    """

    _day_count_factor = day_count_factor(start=issue, end=settlement, basis=basis, next_=first_interest, freq=frequency)

    # Use interest formula
    return par * rate * _day_count_factor


def price(settlement : datetime.date, maturity : datetime.date, rate : float, yld : float, redemption : float, frequency : int, basis : int = 0) -> float:
    """
    Returns the price per $100 face value of a bond.

    Parameters
    ----------
    settlement : datetime.date
        The bond's settlement date.
    maturity : datetime.date
        The bonds's maturity date (when it expires).
    rate : float
        The bond's annual coupon rate.
    yld : float
        The bond's annual yield.
    redemption : float
        The security's redemption value per $100 face value.
    frequency : int
        The number of coupon payments per year.
    basis : int [optional]
        The type of day count basis to use.
            - 0 [default] : US (NASD) 30/360
            - 1 : Actual/Actual
            - 2 : Actual/360
            - 3 : Actual/365
            - 4 : European 30/360

    Returns
    -------
    float
        Price per $100 face value of the bond.
    """

    _PAR = 100

    # Calculate coupon dates
    coupon_dates = [maturity]
    coupon_period = dateutil.relativedelta.relativedelta(months=-MONTHS_IN_YEAR//frequency)
    while coupon_dates[-1] > settlement: # Calculate coupon dates backwards from maturity to issuance
        coupon_dates.append(coupon_dates[-1] + coupon_period)
    coupon_dates = coupon_dates[::-1]
    num_periods = len(coupon_dates) - 1 # First coupon date is before settlement

    # Calculate cash flows
    cash_flows = np.array([_PAR * rate / frequency] * num_periods) # Coupon payments
    cash_flows[-1] += redemption # Principal repayment

    # Calculate discount rates
    discount_rates = np.array([1 + yld / frequency] * num_periods)
    time_to_next = 1 - frequency * day_count_factor(start=coupon_dates[0], end=settlement, basis=basis, next_=coupon_dates[1], freq=frequency)
    discount_rate_powers = -1 * np.array([i + time_to_next for i in range(num_periods)])
    discount_factors = np.power(discount_rates, discount_rate_powers)

    # Calculate dirty price
    transaction_price = np.dot(cash_flows, discount_factors)

    # Calculate clean price
    _accrint = accrint(issue=coupon_dates[0], first_interest=coupon_dates[1], settlement=settlement, rate=rate, par=_PAR, frequency=frequency, basis=basis)
    clean_price = transaction_price - _accrint
    
    return clean_price


def yield_():
    pass
