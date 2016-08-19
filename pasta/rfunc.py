# coding=utf-8
import numpy as np
import pandas as pd
from scipy.special import gammainc, gammaincinv, k0, exp1

"""
rfunc module.
Contains classes for the response functions.
Each response function class needs the following:
"""

_class_doc = """
Attributes
----------
nparam: integer
    number of parameters.
cutoff: float
    percentage after which the step function is cut off.

Functions
---------
set_parameters(self, name)
    A function that returns a Pandas DataFrame of the parameters of the
    response function. Columns of the dataframe need to be
    ['initial', 'pmin', 'pmax', 'vary'].
    Rows of the DataFrame have names of the parameters.
    Input name is used as a prefix.
    This function is called by a Tseries object.
step(self, p)
    Returns an array of the step response. Input
    p is a numpy array of parameter values in the same order as
    defined in set_parameters.
block(self, p)
    Returns an array of the block response. Input
    p is a numpy array of parameter values in the same order as
    defined in set_parameters.

More information on how to write a response class can be found here:
http://pasta.github.io/pasta/developers.html
"""


class Gamma:
    __doc__ = """
    Gamma response function with 3 parameters A, a, and n.

    step(t) = A * Gammainc(n, t / a)

    %(doc)s
    """ % {'doc': _class_doc}

    def __init__(self, cutoff=0.99):
        self.nparam = 3
        self.cutoff = cutoff

    def set_parameters(self, name):
        parameters = pd.DataFrame(columns=['initial', 'pmin', 'pmax', 'vary', 'name'])
        parameters.loc[name + '_A'] = (500.0, 0.0, 5000.0, 1, name)
        parameters.loc[name + '_n'] = (1.0, 0.0, 5.0, 1, name)
        parameters.loc[name + '_a'] = (100.0, 1.0, 5000.0, 1, name)
        return parameters

    def step(self, p):
        self.tmax = gammaincinv(p[1], self.cutoff) * p[2]
        t = np.arange(1.0, self.tmax)
        s = p[0] * gammainc(p[1], t / p[2])
        return s

    def block(self, p):
        s = self.step(p)
        return s[1:] - s[:-1]


class Exponential:
    __doc__ = """
    Exponential response function with 2 parameters: A and a.

    .. math:: step(t) = A * (1 - exp(-t / a))

    %(doc)s
    """ % {'doc': _class_doc}

    def __init__(self, cutoff):
        self.nparam = 2
        self.cutoff = cutoff

    def set_parameters(self, name):
        parameters = pd.DataFrame(columns=['initial', 'pmin', 'pmax', 'vary', 'name'])
        parameters.loc[name + '_A'] = (500.0, 0.0, 5000.0, 1, name)
        parameters.loc[name + '_a'] = (100.0, 1.0, 5000.0, 1, name)
        parameters['tseries'] = name
        return parameters

    def step(self, p):
        self.tmax = -np.log(1.0 / p[1]) * p[1]
        t = np.arange(1.0, self.tmax)
        s = p[0] * (1.0 - np.exp(-t / p[1]))
        return s

    def block(self, p):
        s = self.step(p)
        return s[1:] - s[:-1]


class Hantush:
    """ The Hantush well function

    References
    ----------
    [1] Hantush, M. S., & Jacob, C. E. (1955). Non‐steady radial flow in an
    infinite leaky aquifer. Eos, Transactions American Geophysical Union, 36(1),
    95-100.

    [2] Veling, E. J. M., & Maas, C. (2010). Hantush well function revisited.
    Journal of hydrology, 393(3), 381-388.

    [3] Von Asmuth, J. R., Maas, K., Bakker, M., & Petersen, J. (2008). Modeling
    time series of ground water head fluctuations subjected to multiple stresses.
    Ground Water, 46(1), 30-40.

    """

    def __init__(self, cutoff):
        self.nparam = 3
        self.cutoff = cutoff

    def set_parameters(self, name):
        parameters = pd.DataFrame(columns=['initial', 'pmin', 'pmax', 'vary', 'name'])
        parameters.loc[name + '_S'] = (0.0, 1e-3, 1.0, 1, name)
        parameters.loc[name + '_T'] = (0.0, 10.0, 5000.0, 1, name)
        parameters.loc[name + '_c'] = (0.0, 1000.0, 5000.0, 1, name)
        parameters['tseries'] = name
        return parameters

    def step(self, p, r):
        self.tmax = 10000  # This should be changed with some analytical expression
        t = np.arange(1.0, self.tmax)
        rho = r / np.sqrt(p[1] * p[2])
        tau = np.log(2.0 / rho * t / (p[0] * p[2]))
        # tau[tau > 100] = 100
        h_inf = k0(rho)
        expintrho = exp1(rho)
        w = (expintrho - h_inf) / (expintrho - exp1(rho / 2.0))
        I = h_inf - w * exp1(rho / 2.0 * np.exp(abs(tau))) + (w - 1.0) * \
                                                             exp1(
                                                                 rho * np.cosh(tau))
        s = h_inf + np.sign(tau) * I
        return s

    def block(self, p, r):
        s = self.step(p, r)
        return s[1:] - s[:-1]


class Theis:
    """ The Theis well function

    References
    ----------
    [1] Theis, C. V. (1935). The relation between the lowering of the Piezometric
    surface and the rate and duration of discharge of a well using ground‐water
    storage. Eos, Transactions American Geophysical Union, 16(2), 519-524.

    """

    def __init__(self, cutoff):
        self.nparam = 3
        self.cutoff = cutoff

    def set_parameters(self, name):
        parameters = pd.DataFrame(columns=['initial', 'pmin', 'pmax', 'vary', 'name'])
        parameters.loc[name + '_S'] = (0.0, 3e-1, 1.0, 1, name)
        parameters.loc[name + '_T'] = (0.0, 10.0, 5000.0, 1, name)
        return parameters

    def step(self, p, r):
        self.tmax = 10000  # This should be changed with some analytical expression
        t = np.arange(1.0, self.tmax)
        u = r ** 2.0 * p[0] / (4.0 * p[1] * t)
        s = exp1(u)
        return s

    def block(self, p, r):
        s = self.step(p, r)
        return s[1:] - s[:-1]
    
class One:
    """Dummy class for Constant. Returns 1
    """
    
    def __init__(self, cutoff):
        self.nparam = 1
        self.cutoff = cutoff
        
    def step(self, p):
        return p[0] * np.ones(2)
    
    def block(self, p):
        return p[0] * np.ones(2)
