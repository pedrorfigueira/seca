"""
Gaia DR3 interface for SECA.

This module provides utilities to retrieve stellar parameters
from the Gaia DR3 archive.

Pedro Figueira
"""

import numpy as np
import time

from astroquery.gaia import Gaia

from .config import MAX_RETRIES, RETRY_DELAY

# ----------------------------------------------------------------------
# Gaia DR3 query
# ----------------------------------------------------------------------

def _is_invalid_value(value):
    """
    Return True if an Astropy/NumPy value is missing, masked,
    non-numeric, or non-finite.
    """

    if value is None:
        return True

    if np.ma.is_masked(value):
        return True

    try:
        return not np.isfinite(float(value))
    except (TypeError, ValueError):
        return True

def get_gaia_parameters(source_id):
    """
    Retrieve stellar parameters from Gaia DR3.

    Parameters
    ----------
    source_id : int or str
        Gaia DR3 source identifier.

    Returns
    -------
    dict
        Stellar parameters suitable for ``seca.classify_star``:

        ``source_id``
            Gaia DR3 source identifier.

        ``mass``
            Stellar mass [Msun].

        ``radius``
            Stellar radius [Rsun].

        ``teff``
            Effective temperature [K].

        ``emass``
            Mass uncertainty [Msun].

        ``eradius``
            Radius uncertainty [Rsun].

        ``eteff``
            Effective-temperature uncertainty [K].

        ``flame_flag``
            Gaia DR3 FLAME quality flag. Recommended values
            for SECA are ``"00"`` and ``"01"``.

    Raises
    ------
    RuntimeError
        If the Gaia source cannot be found or required parameters
        are unavailable.
    """

    # --------------------------------------------------------------
    # Validate source identifier
    # --------------------------------------------------------------

    try:
        source_id = int(source_id)

    except (TypeError, ValueError) as exc:

        raise ValueError(
            f"Invalid Gaia DR3 source_id: {source_id}"
        ) from exc

    # --------------------------------------------------------------
    # Gaia query
    # --------------------------------------------------------------

    query = f"""
    SELECT
        gaia.source_id,

        ap.mass_flame,
        ap.mass_flame_lower,
        ap.mass_flame_upper,

        ap.radius_flame,
        ap.radius_flame_lower,
        ap.radius_flame_upper,

        ap.flags_flame,

        gaia.teff_gspphot

    FROM gaiadr3.gaia_source AS gaia

    JOIN gaiadr3.astrophysical_parameters AS ap
        USING (source_id)

    WHERE gaia.source_id = {source_id}
    """

    last_exception = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            job = Gaia.launch_job(query)
            table = job.get_results()

            break

        except Exception as exc:

            last_exception = exc

            if attempt < MAX_RETRIES:

                print(
                    f"Gaia query failed for source {source_id} "
                    f"(attempt {attempt}/{MAX_RETRIES}); "
                    f"retrying in {RETRY_DELAY:.0f} s..."
                )

                time.sleep(RETRY_DELAY)

            else:

                raise RuntimeError(
                    f"Gaia DR3 query failed for source {source_id} "
                    f"after {MAX_RETRIES} attempts."
                ) from last_exception

    if len(table) == 0:

        raise RuntimeError(
            f"Gaia DR3 source {source_id} was not found."
        )

    row = table[0]

    # --------------------------------------------------------------
    # Check required parameters
    # --------------------------------------------------------------

    required = {
        "mass": row["mass_flame"],
        "radius": row["radius_flame"],
        "teff": row["teff_gspphot"],
    }

    for name, value in required.items():

        if _is_invalid_value(value):
            raise RuntimeError(
                f"Gaia DR3 source {source_id} has no valid {name}."
            )

    # --------------------------------------------------------------
    # FLAME quality flag
    # --------------------------------------------------------------

    flame_flag = row["flags_flame"]

    if flame_flag is None:

        flame_flag = None

    else:

        flame_flag = str(flame_flag).strip()

        # Astropy tables can sometimes represent missing
        # string values as masked values.
        if flame_flag in ("--", "nan", "None"):

            flame_flag = None

    # --------------------------------------------------------------
    # Convert asymmetric uncertainties to symmetric uncertainties
    # --------------------------------------------------------------

    mass_lower = row["mass_flame_lower"]
    mass_upper = row["mass_flame_upper"]

    radius_lower = row["radius_flame_lower"]
    radius_upper = row["radius_flame_upper"]

    # --------------------------------------------------------------
    # Mass uncertainty
    # --------------------------------------------------------------

    if _is_invalid_value(mass_lower) or _is_invalid_value(mass_upper) :

        emass = None

    else:

        emass = (float(mass_upper) - float(mass_lower)) / 2.0

        if not np.isfinite(emass) or emass < 0:
            emass = None

    # --------------------------------------------------------------
    # Radius uncertainty
    # --------------------------------------------------------------

    if _is_invalid_value(radius_lower) or _is_invalid_value(radius_upper):

        eradius = None

    else:

        eradius = (float(radius_upper) - float(radius_lower)) / 2.0

        if not np.isfinite(eradius) or eradius < 0:
            eradius = None

    # --------------------------------------------------------------
    # Teff uncertainty
    # --------------------------------------------------------------

    # Gaia DR3 does not provide lower/upper GSP-Phot Teff
    # uncertainties in the columns queried here

    eteff = None

    # --------------------------------------------------------------
    # Return
    # --------------------------------------------------------------

    return {
        "source_id": source_id,

        "mass": float(row["mass_flame"]),
        "radius": float(row["radius_flame"]),
        "teff": float(row["teff_gspphot"]),

        "emass": emass,
        "eradius": eradius,
        "eteff": eteff,

        "flame_flag": flame_flag,
    }
