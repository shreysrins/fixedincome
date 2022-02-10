"""
Fixed income analytics (general)
"""


import numpy as np
import scipy.optimize


def npv(rate : float, values : np.ndarray) -> float:
    """
    Calculates the Net Present Value (NPV) of a series of cash flows.

    Parameters
    ----------
    rate : float
        The (simple) discount rate over the length of one period.
    values : np.ndarray
        Correspond to payments and income per period, in order.

    Returns
    -------
    float
        The NPV of the given series of cash flows, discounted at the given rate.
    """

    weights = np.fromfunction(function=lambda i: 1/(1 + rate)**(i + 1), shape=(values.size,), dtype=int)
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


def rate(nper : int, pmt : float, pv : float, fv : float = 0, guess : float = 0.1) -> float:
    """
    Calculates the interest rate per period of an annuity.

    Parameters
    ----------
    nper : int
        The total number of payment periods in an annuity.
    pmt : float
        The constant payment amount made each period.
    pv : float
        The present value (i.e., total amount that a series of payments is worth now) of the annuity.
    fv : float [optional]
        The future value (i.e., cash balance to be attained after the last payment is made) of the annuity.
    guess : float [optional]
        An initial guess for the interest rate.

    Returns
    -------
    float
        The interest rate per period of the annuity.
    """

    cash_flows = np.array([-1 * pv] + [pmt] * nper, dtype=float)
    cash_flows[-1] += fv

    return irr(values=cash_flows, guess=guess)
