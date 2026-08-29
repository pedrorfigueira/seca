"""
Asteroseismic scaling relations used by SECA.

Pedro Figueira
"""

import numpy as np

from .calibration import (
    DNU_SUN, NUMAX_SUN, TEFF_SUN)

# ----------------------------------------------------------------------
# Scaling relations
# ----------------------------------------------------------------------

def delta_nu(mass, radius):
    """
    Compute the large frequency separation.

    Parameters
    ----------
    mass : float
        Stellar mass [Msun]

    radius : float
        Stellar radius [Rsun]

    Returns
    -------
    float
        Δν [μHz]
    """

    return DNU_SUN * np.sqrt(mass) / radius**1.5


def numax(mass, radius, teff):
    """
    Compute the frequency of maximum oscillation power.

    Parameters
    ----------
    mass : float
        Stellar mass [Msun]

    radius : float
        Stellar radius [Rsun]

    teff : float
        Effective temperature [K]

    Returns
    -------
    float
        νmax [μHz]
    """

    return NUMAX_SUN * mass / radius**2 / np.sqrt(teff / TEFF_SUN)



def seismic_parameters(mass, radius, teff):
    """
    Compute both seismic quantities.

    Returns
    -------
    tuple
        (Δν, νmax)
    """

    return (
        delta_nu(mass, radius),
        numax(mass, radius, teff),
    )


# ----------------------------------------------------------------------
# Error propagation - not used in current version
# ----------------------------------------------------------------------

def delta_nu_error(
    mass,
    radius,
    emass,
    eradius,
):
    """
    Propagate uncertainties to Δν.

    Parameters
    ----------
    emass : float
        Mass uncertainty [Msun]

    eradius : float
        Radius uncertainty [Rsun]

    Returns
    -------
    float
        σ(Δν) [μHz]
    """

    dnu = delta_nu(mass, radius)

    frac = np.sqrt(
        0.25 * (emass / mass) ** 2
        +
        2.25 * (eradius / radius) ** 2
    )

    return dnu * frac


def numax_error(
    mass,
    radius,
    teff,
    emass,
    eradius,
    eteff,
):
    """
    Propagate uncertainties to νmax.

    Parameters
    ----------
    emass : float
        Mass uncertainty [Msun]

    eradius : float
        Radius uncertainty [Rsun]

    eteff : float
        Effective-temperature uncertainty [K]

    Returns
    -------
    float
        σ(νmax) [μHz]
    """

    nm = numax(mass, radius, teff)

    frac = np.sqrt(
        (emass / mass) ** 2
        +
        4.0 * (eradius / radius) ** 2
        +
        0.25 * (eteff / teff) ** 2
    )

    return nm * frac


def propagate_errors(
    mass,
    radius,
    teff,
    emass,
    eradius,
    eteff,
):
    """
    Propagate stellar-parameter uncertainties to the
    asteroseismic quantities.

    Returns
    -------
    tuple
        (σΔν, σνmax)
    """

    return (

        delta_nu_error(
            mass,
            radius,
            emass,
            eradius,
        ),

        numax_error(
            mass,
            radius,
            teff,
            emass,
            eradius,
            eteff,
        ),
    )

def meets_precision_requirement(
    mass,
    radius,
    teff,
    emass,
    eradius,
    eteff,
):
    """
    Check whether the propagated uncertainties satisfy
    the SECA calibration precision.

    Returns
    -------
    bool
    """

    sdnu, snumax = propagate_errors(
        mass,
        radius,
        teff,
        emass,
        eradius,
        eteff,
    )

    return (
        sdnu <= CALIBRATION_DNU_ERROR
        and
        snumax <= CALIBRATION_NUMAX_ERROR
    )
