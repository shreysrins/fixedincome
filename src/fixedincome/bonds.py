"""
Fixed income analytics for bonds

Implements various functions useful for bond analytics.
"""


import datetime


def accrint(issue : datetime.date, first_interest : datetime.date, settlement : datetime.date, rate : float, par : float, frequency : int, basis : int = 2, calc_method : bool = True) -> float:
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
            - 2 [default] : Actual/360
            - 3 : Actual/365
    calc_method : bool [optional]
        The way to calculate the total accrued interest when the date of settlement is later than the date of first_interest.
            - True [default] : calculate the total accrued interest from issue to settlement.
            - False : calculate the accrued interest from first_interest to settlement.

    Returns
    -------
    float
        Accrued interest of the bond.
    """

    if basis == 2:
        days_in_year = 360
    elif basis == 3:
        days_in_year = 365
    else:
        raise ValueError

    if settlement <= first_interest:
        w = (first_interest - settlement).days / (days_in_year / frequency)
        return (1 - w) * (rate / frequency) * par
    else:
        if calc_method:
            w = (first_interest - settlement).days / (days_in_year / frequency)
        return (1 - w) * (rate / frequency) * par


    pass


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


def bondYield():
    pass
