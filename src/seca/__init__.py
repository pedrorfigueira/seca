"""
SECA
Stellar Evolutionary Classification with Asteroseismology

A lightweight Python package for the asteroseismic classification
of main-sequence, subgiant and red giant branch stars.
"""

__version__ = "1.0.0"

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
    propagate_errors,
    meets_precision_requirement,
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
    "propagate_errors",
    "meets_precision_requirement",

    # Output class
    "StellarClassification",
]