"""
Fixed income analytics for bonds

Implements various functions useful for bond analytics.
"""


import datetime
from typing import List

import dateutil.relativedelta
import numpy as np
import scipy.optimize

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


def coupon_dates(settlement : datetime.date, maturity : datetime.date, frequency : int) -> List[datetime.date]:
    """
    Returns the coupon dates for a bond from settlement to maturity.

    Parameters
    ----------
    settlement : datetime.date
        The bond's settlement date.
    maturity : datetime.date
        The bonds's maturity date (when it expires).
    frequency : int
        The number of coupon payments per year.

    Returns
    -------
    list[datetime.date]
        Coupon dates of the bond.
    """

    _coupon_dates = [maturity]

    # Calculate length of coupon period in months
    coupon_period = dateutil.relativedelta.relativedelta(months=-MONTHS_IN_YEAR//frequency)

    # Calculate coupon dates backwards from maturity to issuance
    while _coupon_dates[-1] > settlement:
        _coupon_dates.append(_coupon_dates[-1] + coupon_period)
    
    # Return list in chronological order
    _coupon_dates = _coupon_dates[::-1]
    return _coupon_dates


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
    _coupon_dates = coupon_dates(settlement=settlement, maturity=maturity, frequency=frequency)
    num_periods = len(_coupon_dates) - 1 # First coupon date is before settlement

    # Calculate cash flows
    cash_flows = np.array([_PAR * rate / frequency] * num_periods) # Coupon payments
    cash_flows[-1] += redemption # Principal repayment

    # Calculate discount rates
    discount_rates = np.array([1 + yld / frequency] * num_periods)
    time_to_next = 1 - frequency * day_count_factor(start=_coupon_dates[0], end=settlement, basis=basis, next_=_coupon_dates[1], freq=frequency)
    discount_rate_powers = -1 * np.array([i + time_to_next for i in range(num_periods)])
    discount_factors = np.power(discount_rates, discount_rate_powers)

    # Calculate dirty price
    transaction_price = np.dot(cash_flows, discount_factors)

    # Calculate clean price
    _accrint = accrint(issue=_coupon_dates[0], first_interest=_coupon_dates[1], settlement=settlement, rate=rate, par=_PAR, frequency=frequency, basis=basis)
    clean_price = transaction_price - _accrint
    
    return clean_price


def yield_(settlement : datetime.date, maturity : datetime.date, rate : float, price_ : float, redemption : float, frequency : int, basis : int = 0):
    """
    Returns the yield for a bond with $100 face value.

    Parameters
    ----------
    settlement : datetime.date
        The bond's settlement date.
    maturity : datetime.date
        The bonds's maturity date (when it expires).
    rate : float
        The bond's annual coupon rate.
    price_ : float
        The bond's quoted clean price.
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
        The annualized per-period bond yield.
    """

    _PAR = 100
    _coupon_dates = coupon_dates(settlement=settlement, maturity=maturity, frequency=frequency)

    # Special case for when no remaining coupons to be paid (only principal)
    if len(_coupon_dates) == 1:
        _day_count_factor = day_count_factor(start=issue, end=settlement, basis=basis, next_=first_interest, freq=frequency)
        return ((redemption/100 + rate/frequency) - (_PAR/100 + (_day_count_factor * rate))) / (_PAR/100 + (_day_count_factor * rate)) * (frequency / (1 - _day_count_factor * frequency))
    else: # Use optimization to identify the yield that matches quoted clean price
        return scipy.optimize.newton(func=lambda y : price(settlement=settlement, maturity=maturity, rate=rate, yld=y, redemption=redemption, frequency=frequency, basis=basis) - price_, x0=rate, tol=0.0000001, maxiter=100)
