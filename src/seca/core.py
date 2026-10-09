"""
Core routines for SECA.

This module provides the high-level interface to the package.

Pedro Figueira
"""

from .scaling import seismic_parameters

from .classification import classify

# ----------------------------------------------------------------------
# High-level interface
# ----------------------------------------------------------------------

def classify_star(
    mass,
    radius,
    teff,
    emass=None,
    eradius=None,
    eteff=None,
    flame_flag=None,
    reference_model="reference",
):
    """
    Classify a star from its fundamental stellar parameters.

    The stellar mass, radius and effective temperature are converted
    into the seismic quantities Δν and νmax using the standard scaling
    relations. The resulting seismic quantities are then classified
    using the mass-dependent evolutionary transition zones.

    Parameters
    ----------
    mass : float
        Stellar mass [Msun].

    radius : float
        Stellar radius [Rsun].

    teff : float
        Effective temperature [K].

    emass : float, optional
        Uncertainty on the stellar mass [Msun].

    eradius : float, optional
        Uncertainty on the stellar radius [Rsun].

    eteff : float, optional
        Uncertainty on the effective temperature [K].

    flame_flag : str, optional
        Gaia FLAME quality flag, when available.

    reference_model : str, optional
        BaSTI calibration used as the reference for classification.
        Defaults to "reference".

    Returns
    -------
    StellarClassification
        Complete SECA classification.
    """

    dnu, numax = seismic_parameters(mass, radius, teff)

    return classify(
        mass=mass,
        radius=radius,
        teff=teff,
        dnu=dnu,
        numax=numax,
        emass=emass,
        eradius=eradius,
        eteff=eteff,
        flame_flag=flame_flag,
        reference_model=reference_model,
    )


# ----------------------------------------------------------------------
# Catalogue interface
# ----------------------------------------------------------------------

def classify_catalog(
    mass,
    radius,
    teff,
    emass=None,
    eradius=None,
    eteff=None,
    reference_model="reference",
):
    """
    Classify a catalogue of stars.

    Parameters
    ----------
    mass : array-like
        Stellar masses [Msun].

    radius : array-like
        Stellar radii [Rsun].

    teff : array-like
        Effective temperatures [K].

    emass, eradius : array-like, optional
        Uncertainties on the stellar mass and radius. They must be
        provided together.

    eteff : array-like, optional
        Uncertainty on the effective temperature.

    reference_model : str, optional
        BaSTI calibration used as the reference for classification.
        Defaults to "reference".

    Returns
    -------
    list of StellarClassification
        Classification results in the same order as the input
        catalogue. One StellarClassification instance is returned
        for each star.
    """

    mass = list(mass)
    radius = list(radius)
    teff = list(teff)

    nstars = len(mass)

    if not (len(radius) == len(teff) == nstars):
        raise ValueError("mass, radius and teff must have the same length.")

    # ----------------------------------------------------------
    # Determine whether uncertainties are being used
    # ----------------------------------------------------------

    use_errors = emass is not None and eradius is not None

    # Mass and radius uncertainties must be supplied together.
    if (emass is None) != (eradius is None):
        raise ValueError("Either provide both emass and eradius or neither.")

    # Teff uncertainty is optional.
    if eteff is not None:
        eteff = list(eteff)

        if len(eteff) != nstars:
            raise ValueError(
                "eteff must have the same length as the stellar parameters."
            )

    if use_errors:
        emass = list(emass)
        eradius = list(eradius)

        if not (len(emass) == len(eradius) == nstars):
            raise ValueError(
                "emass and eradius must have the same length as the stellar parameters."
            )

    # ----------------------------------------------------------
    # Classify stars
    # ----------------------------------------------------------

    results = []

    for i in range(nstars):
        result = classify_star(
            mass=mass[i],
            radius=radius[i],
            teff=teff[i],
            emass=emass[i] if use_errors else None,
            eradius=eradius[i] if use_errors else None,
            eteff=eteff[i] if eteff is not None else None,
            reference_model=reference_model,
        )

        results.append(result)

    return results
