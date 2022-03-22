"""
Fixed income analytics for the yield curve

Implements various functions useful for yield curve analytics.
"""


import numpy as np


def bootstrap(cash_flows : np.ndarray, prices : np.ndarray) -> np.ndarray:
    """
    Calculates the spot yield curve from a series of bonds. 
    
    Parameters
    ----------
    cash_flows : np.ndarray
        Nonsingular payoff matrix of a series of bonds.
    prices : np.ndarray
        Corresponding price of each bond.
    
    Returns
    -------
    np.ndarray
        The corresponding spot yield curve derived from no-arbitrage relationships.
    """
    
    assert cash_flows.shape[1] == prices.shape[0], "Check shapes of input matrices."

    discount_factors = np.linalg.inv(cash_flows) @ prices
    yields = np.power(discount_factors, np.reshape(-1 / np.arange(start=1, stop=discount_factors.shape[0]+1), newshape=discount_factors.shape)) - 1 # Formula: d = 1/(1 + y)^i
    return np.reshape(yields, newshape=(yields.shape[0])) # Flatten output


def regression():
    raise NotImplementedError("Regression not yet implemented.")


def spline():
    raise NotImplementedError("Spline not yet implemented.")


def nelson_siegel():
    raise NotImplementedError("Nelson-Siegel not yet implemented.")
