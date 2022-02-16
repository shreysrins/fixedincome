"""
Fixed income analytics for bonds

Implements various functions useful for bond analytics.
"""


import datetime
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

    return par * rate * _day_count_factor


def price(settlement : datetime.date, maturity : datetime.date, rate : float, yld : float, redemption : float, frequency : int, basis : int = 2) -> float:
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
            - 2 [default] : Actual/360
            - 3 : Actual/365

    Returns
    -------
    float
        Price per $100 face value of the bond.
    """
    pass


def yield_():
    pass
