"""
SECA
Stellar Evolutionary Classification with Asteroseismology

A lightweight Python package for the asteroseismic classification
of main-sequence, subgiant and red giant branch stars.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("seca")
except PackageNotFoundError:
    __version__ = "0+unknown"

# ----------------------------------------------------------------------
# High-level interface
# ----------------------------------------------------------------------

from .core import classify_star, classify_catalog

# Convenience alias
classify = classify_star

# ----------------------------------------------------------------------
# Scaling relations
# ----------------------------------------------------------------------

from .scaling import (
    delta_nu,
    numax,
    seismic_parameters,
    delta_nu_error,
    numax_error,
    seismic_parameter_errors,
)

# ----------------------------------------------------------------------
# Output class
# ----------------------------------------------------------------------

from .classification import StellarClassification

# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

__all__ = [
    # High-level interface
    "classify",
    "classify_star",
    "classify_catalog",

    # Scaling relations
    "delta_nu",
    "numax",
    "seismic_parameters",
    "delta_nu_error",
    "numax_error",
    "seismic_parameter_errors",

    # Output class
    "StellarClassification",
]
