"""
SIMBAD interface for SECA.

Utilities for resolving SIMBAD identifiers to Gaia DR3 source IDs.

Pedro Figueira
"""

import time

from astroquery.simbad import Simbad

from .config import MAX_RETRIES, RETRY_DELAY

# ----------------------------------------------------------------------
# SIMBAD identifier resolution
# ----------------------------------------------------------------------

def get_gaia_source_id(identifier):
    """
    Resolve a SIMBAD identifier to a Gaia DR3 source ID.

    Parameters
    ----------
    identifier : str
        SIMBAD identifier.

    Returns
    -------
    int
        Gaia DR3 source identifier.

    Raises
    ------
    RuntimeError
        If the SIMBAD query fails repeatedly or no Gaia DR3
        identifier can be found.
    """

    identifier = str(identifier).strip()

    # --------------------------------------------------------------
    # Query SIMBAD with retries
    # --------------------------------------------------------------

    last_exception = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            result = Simbad.query_objectids(identifier)

            break

        except Exception as exc:

            last_exception = exc

            if attempt < MAX_RETRIES:

                print(
                    f"SIMBAD query failed for {identifier} "
                    f"(attempt {attempt}/{MAX_RETRIES}); "
                    f"retrying in {RETRY_DELAY:.0f} s..."
                )

                time.sleep(RETRY_DELAY)

            else:

                raise RuntimeError(
                    f"SIMBAD query failed for identifier "
                    f"{identifier} after {MAX_RETRIES} attempts."
                ) from last_exception

    # --------------------------------------------------------------
    # Check result
    # --------------------------------------------------------------

    if result is None or len(result) == 0:

        raise RuntimeError(
            f"SIMBAD identifier {identifier} "
            "could not be resolved."
        )

    # --------------------------------------------------------------
    # Find Gaia DR3 identifier
    # --------------------------------------------------------------

    gaia_ids = []

    for row in result:

        value = str(
            row["id"]
        ).strip()

        if value.startswith("Gaia DR3"):

            try:

                gaia_id = int(
                    value.split()[-1]
                )

                gaia_ids.append(gaia_id)

            except ValueError:

                continue

    if not gaia_ids:

        raise RuntimeError(
            f"SIMBAD identifier {identifier} "
            "has no Gaia DR3 source identifier."
        )

    # Return the first Gaia DR3 match
    return gaia_ids[0]