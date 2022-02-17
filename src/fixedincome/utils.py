"""
Fixed income analytics (general)

Implements various generic functions useful for fixed income applications.
"""


import datetime

import numpy as np
import scipy.optimize


MONTHS_IN_YEAR = 12


def npv(rate_ : float, values : np.ndarray) -> float:
    """
    Calculates the Net Present Value (NPV) of a series of cash flows.

    Parameters
    ----------
    rate_ : float
        The (simple) discount rate over the length of one period.
    values : np.ndarray
        Correspond to payments and income per period, in order.

    Returns
    -------
    float
        The NPV of the given series of cash flows, discounted at the given rate.
    """

    weights = np.fromfunction(function=lambda i: 1/(1 + rate_)**(i + 1), shape=(values.size,), dtype=int)
    return np.dot(values, weights)


def irr(values: np.ndarray, guess : float = 0.1) -> float:
    """
    Calculates the Internal Rate of Return (IRR) for a series of cash flows.

    Parameters
    ----------
    values : np.ndarray
        A series of cash flows, in order.
    guess : float [optional]
        An initial guess for the IRR.

    Returns
    -------
    float
        The IRR of the given series of cash flows.
    """

    return scipy.optimize.newton(func=npv, x0=guess, args=(values,), tol=0.0000001, maxiter=20)


def rate(nper : int, pmt : float, pv_ : float, fv_ : float = 0, guess : float = 0.1) -> float:
    """
    Calculates the interest rate per period of an annuity.

    Parameters
    ----------
    nper : int
        The total number of payment periods in an annuity.
    pmt : float
        The constant payment amount made each period.
    pv_ : float
        The present value (i.e., total amount that a series of payments is worth now) of the annuity.
    fv_ : float [optional]
        The future value (i.e., cash balance to be attained after the last payment is made) of the annuity.
    guess : float [optional]
        An initial guess for the interest rate.

    Returns
    -------
    float
        The interest rate per period of the annuity.
    """

    cash_flows = np.array([pv_] + [pmt] * nper, dtype=float)
    cash_flows[-1] += fv_

    return irr(values=cash_flows, guess=guess)


def pv(rate_ : float, nper : int, pmt : float, fv_ : float = 0, type_ : int = 0) -> float:
    """
    Calculates the present value of a loan based on a constant interest rate.

    Parameters
    ----------
    rate_ : float
        The interest rate per period.
    nper : int
        The total number of payment periods in an annuity.
    pmt : float
        The constant payment amount made each period.
    fv_ : float [optional]
        The future value (i.e., cash balance to be attained after the last payment is made) of the annuity.
    type_ : int [optional]
        Indicates when payments are due.
            - 0 [default] : at the end of the period.
            - 1 : at the beginning of the period

    Returns
    -------
    float
        The present value of the loan based on a constant interest rate.
    """
    
    if rate != 0:
        _pv = -(pmt*(1 + rate_*type_)*(((1 + rate_)**nper - 1)/rate_) + fv_)/((1 + rate_)**nper)
    else:
        _pv = -(pmt*nper + fv_)

    return _pv


def fv(rate_ : float, nper : int, pmt : float, pv_ : float = 0, type_ : int = 0) -> float:
    """
    Calculates the future value of a loan based on a constant interest rate.

    Parameters
    ----------
    rate_ : float
        The interest rate per period.
    nper : int
        The total number of payment periods in an annuity.
    pmt : float
        The constant payment amount made each period.
    pv_ : float [optional]
        The present value of the annuity.
    type_ : int [optional]
        Indicates when payments are due.
            - 0 [default] : at the end of the period.
            - 1 : at the beginning of the period

    Returns
    -------
    float
        The future value of the loan based on a constant interest rate.
    """
    
    if rate_ != 0:
        _fv = -(pv_*(1 + rate_)**nper + pmt*(1 + rate_*type_)*(((1 + rate_)**nper - 1)/rate_))
    else:
        _fv = -(pmt*nper + pv_)

    return _fv


def _thirty_threesixty_day_count_factor(start : datetime.date, end : datetime.date) -> float:
    """Calculate day count factor on a 30/360 basis (after date adjustments)."""
    return (360 * (end.year - start.year) + 30 * (end.month - start.month) + (end.day - start.day)) / 360


def day_count_factor(start : datetime.date, end : datetime.date, basis : int = 0, next_ : datetime.date = None, freq : int = None) -> float:
    """
    Calculates the day count factor between dates for measuring interest accrual.

    Parameters
    ----------
    start : datetime.date
        The starting date of the interest period.
    end : datetime.date
        The ending date of the accrual period.
    basis : int [optional]
        The type of day count basis to use.
            - 0 [default] : US (NASD) 30/360
            - 1 : Actual/Actual
            - 2 : Actual/360
            - 3 : Actual/365
            - 4 : European 30/360
    next_ : datetime.date [optional, required when basis == 1]
        The ending date of the interest period, or starting date of the next interest period. This argument is required for the Actual/Actual basis.
    freq : int [optional, required when basis == 1]
        The number of interest payment periods in a full year.

    Returns
    -------
    float
        The day count factor, or percentage of interest that has linearly accrued, for the interest payment period.
    """

    # Switch calculation methodology by specified basis
    if basis == 0: # US (NASD) 30/360
        # Date adjustments
        if end.day == 31 and (start.day == 30 or start.day == 31):
            end = end.replace(day=30)
        if start.day == 31:
            start = start.replace(day=30)
        return _thirty_threesixty_day_count_factor(start=start, end=end)
    elif basis == 1: # Actual/Actual
        assert next_, "Valid date of next coupon payment required for Actual/Actual basis"
        assert freq and (freq > 0), "Valid number of annual coupon payments required for Actual/Actual basis"
        return (end - start).days / (freq * (next_ - start).days)
    elif basis == 2: # Actual/360
        return (end - start).days / 360.0
    elif basis == 3: # Actual/365
        return (end - start).days / 365.0
    elif basis == 4: # European 30/360
        # Date adjustments
        if start.day == 31:
            start = start.replace(day=30)
        if end.day == 31:
            end = end.replace(day=30)
        return _thirty_threesixty_day_count_factor(start=start, end=end)
    else: # Basis misspecified
        raise ValueError("Invalid basis specified.")
