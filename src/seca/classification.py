"""
Classification routines for SECA.

This module implements the evolutionary classification based on the
calibrated transition frequencies described in the accompanying paper.

Pedro Figueira
"""

import numpy as np

from dataclasses import dataclass
from typing import Optional

from .calibration import (
    BASTI_COEFFICIENTS,
    MIN_CALIBRATION_MASS,
    MAX_CALIBRATION_MASS,
)

from .scaling import seismic_parameter_errors

# ----------------------------------------------------------------------
# Classification class
# ----------------------------------------------------------------------

@dataclass
class StellarClassification:
    """
    Output of a SECA stellar evolutionary classification.
    """

    # ----------------------------------------------------------
    # Input stellar parameters
    # ----------------------------------------------------------

    mass: float
    radius: float
    teff: float

    # ----------------------------------------------------------
    # Input stellar-parameter uncertainties
    # ----------------------------------------------------------

    emass: Optional[float] = None
    eradius: Optional[float] = None
    eteff: Optional[float] = None

    # ----------------------------------------------------------
    # Gaia FLAME quality
    # ----------------------------------------------------------

    flame_flag: Optional[str] = None
    flame_quality_ok: Optional[bool] = None

    # ----------------------------------------------------------
    # Derived seismic quantities
    # ----------------------------------------------------------

    dnu: float = 0.0
    numax: float = 0.0

    sigma_dnu: Optional[float] = None
    sigma_numax: Optional[float] = None

    # ----------------------------------------------------------
    # Individual classifications
    # ----------------------------------------------------------

    dnu_stage: str = ""
    numax_stage: str = ""

    # ----------------------------------------------------------
    # Final classification
    # ----------------------------------------------------------

    stage: Optional[str] = None
    is_consistent: bool = False

    # ----------------------------------------------------------
    # Model-dependent warnings
    # ----------------------------------------------------------

    model_warnings: tuple = ()

    # ----------------------------------------------------------
    # Mass-offset diagnostic
    # ----------------------------------------------------------

    mass_offset_warning: bool = False

    # ----------------------------------------------------------
    # Parameter-uncertainty warnings
    # ----------------------------------------------------------

    # Each entry is (quantity, direction, alternative_stage).
    parameter_warnings: tuple = ()

    mass_range_ok: bool = True

    # Calibration used for the nominal classification
    reference_model: str = "reference"

    @property
    def mass_fractional_error(self):
        """Fractional uncertainty on stellar mass."""

        if self.emass is None:
            return None

        return self.emass / self.mass

    @property
    def radius_fractional_error(self):
        """Fractional uncertainty on stellar radius."""

        if self.eradius is None:
            return None

        return self.eradius / self.radius

    def __str__(self):

        text = (
            "SECA Stellar Classification\n"
            "---------------------------\n"
            f"Reference calibration : {self.reference_model}\n"
            f"Mass                 : {self.mass:.3f} M⊙\n"
            f"Radius               : {self.radius:.3f} R⊙\n"
            f"Teff                 : {self.teff:.0f} K\n"
            f"Δν                   : {self.dnu:.2f} μHz\n"
            f"νmax                 : {self.numax:.2f} μHz\n"
        )

        if self.sigma_dnu is not None:

            text += (
                f"σ(Δν)                : "
                f"{self.sigma_dnu:.2f} μHz\n"
            )

        if self.sigma_numax is not None:

            text += (
                f"σ(νmax)              : "
                f"{self.sigma_numax:.2f} μHz\n"
            )

        # ----------------------------------------------------------
        # Parameter uncertainties
        # ----------------------------------------------------------

        text += (
            "\nParameter uncertainties\n"
            "-----------------------\n"
        )

        if self.emass is None:
            text += "Mass uncertainty        : not provided\n"
        else:
            text += (
                f"Mass uncertainty        : "
                f"{self.emass:.4f} Msun "
                f"({100 * self.mass_fractional_error:.1f}%)\n"
            )

        if self.eradius is None:
            text += "Radius uncertainty      : not provided\n"
        else:
            text += (
                f"Radius uncertainty      : "
                f"{self.eradius:.4f} Rsun "
                f"({100 * self.radius_fractional_error:.1f}%)\n"
            )

        if self.eteff is None:
            text += "Teff uncertainty        : not provided\n"
        else:
            text += (
                f"Teff uncertainty        : "
                f"{self.eteff:.1f} K "
                f"({100 * self.eteff / self.teff:.1f}%)\n"
            )

        # ----------------------------------------------------------
        # Mass-range warning
        # ----------------------------------------------------------

        if not self.mass_range_ok:
            text += (
                "\n"
                f"WARNING: Stellar mass ({self.mass:.3f} M⊙) is outside "
                f"the calibrated range "
                f"{MIN_CALIBRATION_MASS:.1f}–{MAX_CALIBRATION_MASS:.1f} M⊙.\n"
                "The SECA classification is an extrapolation.\n"
            )

        # ----------------------------------------------------------
        # Gaia FLAME quality
        # ----------------------------------------------------------

        if self.flame_flag is not None:

            if self.flame_quality_ok:

                text += (
                    "\nFLAME quality\n"
                    "-------------\n"
                    f"flags_flame             : {self.flame_flag}\n"
                    "FLAME quality           : [OK]\n"
                )

            else:

                text += (
                    "\nFLAME quality\n"
                    "-------------\n"
                    f"flags_flame             : {self.flame_flag}\n"
                    "FLAME quality            : [WARNING]\n"
                    "  Recommended values are 00 or 01.\n"
                )

        # ----------------------------------------------------------
        # Model dependence
        # ----------------------------------------------------------

        if self.model_warnings:

            text += (
                "\nModel dependence\n"
                "----------------\n"
                "WARNING: The final classification changes for:\n"
            )

            for model_name, alternative_stage in self.model_warnings:
                text += (
                    f"  {model_name}: classification becomes "
                    f"{alternative_stage}\n"
                )

            text += (
                f"The {self.reference_model} reference classification is retained.\n"
            )

        else:

            text += (
                "\nModel dependence\n"
                "----------------\n"
                f"No alternative calibration changes the classification relative to {self.reference_model}.\n"
            )

        # ----------------------------------------------------------
        # Parameter uncertainty
        # ----------------------------------------------------------

        if self.parameter_warnings:

            text += (
                "\nParameter uncertainty\n"
                "----------------------\n"
                "WARNING: The final classification changes within the 2σ "
                "uncertainty range:\n"
            )

            for quantity, direction, alternative_stage in self.parameter_warnings:
                text += (
                    f"  {quantity}: classification becomes "
                    f"{alternative_stage} at {direction}\n"
                )

            text += (
                "The reference classification is retained.\n"
            )

        else:

            text += (
                "\nParameter uncertainty\n"
                "----------------------\n"
                "No classification change within 2σ uncertainties.\n"
            )

        # ----------------------------------------------------------
        # Mass-offset diagnostic
        # ----------------------------------------------------------

        if self.mass_offset_warning:

            text += (
                "\nMass-offset diagnostic\n"
                "----------------------\n"
                "WARNING: Δν classifies the star as RGB while "
                "νmax classifies it as MS.\n"
                "This combination may indicate a positive offset "
                "in the input stellar mass.\n"
            )

        # ----------------------------------------------------------
        # Classifications
        # ----------------------------------------------------------

        text += (
            "\n"
            f"Δν classification    : {self.dnu_stage}\n"
            f"νmax classification  : {self.numax_stage}\n"
        )

        stage = (
            self.stage
            if self.stage is not None
            else "Not assigned"
        )

        text += (
            f"Final classification : {stage} "
            f"[{'OK' if self.is_consistent else 'WARNING'}]\n"
        )

        # ----------------------------------------------------------
        # Consistency warning
        # ----------------------------------------------------------

        if not self.is_consistent:
            text += "\nWARNING: Δν and νmax classifications are inconsistent.\n"

        # ----------------------------------------------------------
        # Summary
        # ----------------------------------------------------------

        quality_issues = []

        # Mass calibration range
        if not self.mass_range_ok:
            quality_issues.append(
                 "Stellar mass outside the calibrated "
                f"{MIN_CALIBRATION_MASS:.1f}–{MAX_CALIBRATION_MASS:.1f} Msun range"
            )

        # Gaia FLAME quality
        if self.flame_quality_ok is False:
            quality_issues.append(f"FLAME quality flag = {self.flame_flag}")

        # Classification consistency
        if not self.is_consistent:
            quality_issues.append(
                "Δν and νmax classifications are inconsistent"
            )

        # Mass-offset diagnostic
        if self.mass_offset_warning:
            quality_issues.append(
                "Δν = RGB and νmax = MS; possible positive offset "
                "in input stellar mass"
            )

        # Parameter uncertainty
        if self.parameter_warnings:
            quality_issues.append(
                "Classification sensitive to stellar-parameter "
                "uncertainties at the 2σ level"
            )

        text += (
            "\nSummary\n"
            "-------\n"
        )

        if not quality_issues:

            text += f"{stage} star, no warnings\n"

        else:

            text += f"{stage} star, warnings:\n"

            for issue in quality_issues:
                text += f"  - {issue}\n"

        return text

# ----------------------------------------------------------------------
# Polynomial evaluation
# ----------------------------------------------------------------------

def polynomial(coefficients, mass):
    """
    Evaluate a cubic polynomial.

    Parameters
    ----------
    coefficients : iterable
        (a3, a2, a1, a0)

    mass : float
        Stellar mass [Msun]

    Returns
    -------
    float
    """

    return np.polyval(coefficients, mass)


# ----------------------------------------------------------------------
# Transition frequencies
# ----------------------------------------------------------------------

def transition_frequency(
    mass,
    quantity,
    transition,
    model="reference",
):
    """
    Return a single transition frequency for a specified calibration model.

    Parameters
    ----------
    mass : float
        Stellar mass [Msun].

    quantity : str
        "dnu" or "numax".

    transition : str
        "MS-SG" or "SG-RGB".

    model : str
        Calibration model name from BASTI_COEFFICIENTS.

    Returns
    -------
    float
        Transition frequency [μHz].
    """

    coefficients = BASTI_COEFFICIENTS[
        model
    ][transition][quantity]

    return polynomial(
        coefficients,
        mass,
    )

# ----------------------------------------------------------------------
# Individual classifications
# ----------------------------------------------------------------------

def classify_parameter_model(
    value,
    mass,
    quantity,
    model="reference",
):
    """
    Classify one seismic parameter using a specified calibration model.

    The selected reference model defines the nominal SECA
    classification; alternative models are evaluated to assess
    sensitivity to the adopted stellar-evolution calibration.
    """

    ms_sg = transition_frequency(
        mass,
        quantity,
        "MS-SG",
        model=model,
    )

    sg_rgb = transition_frequency(
        mass,
        quantity,
        "SG-RGB",
        model=model,
    )

    if value > ms_sg:
        return "MS"

    if value > sg_rgb:
        return "SG"

    return "RGB"

# ----------------------------------------------------------------------
# Final classification
# ----------------------------------------------------------------------

def combine_classifications(
    dnu_stage,
    numax_stage,
):
    """
    Combine the independent Δν and νmax classifications.

    The individual diagnostics are classified as MS, SG, or RGB.

    When the two classifications agree, that stage is returned.

    When they differ:
        MS + SG  -> MS-SG
        SG + RGB -> SG-RGB
        MS + RGB -> SG
    """

    # Agreement
    if dnu_stage == numax_stage:
        return dnu_stage

    # Adjacent evolutionary stages
    if {
        dnu_stage,
        numax_stage,
    } == {
        "MS",
        "SG",
    }:
        return "MS-SG"

    if {
        dnu_stage,
        numax_stage,
    } == {
        "SG",
        "RGB",
    }:
        return "SG-RGB"

    # The diagnostics span both transitions.
    if {
        dnu_stage,
        numax_stage,
    } == {
        "MS",
        "RGB",
    }:
        return "SG"

    return None

# ----------------------------------------------------------------------
# Complete classification
# ----------------------------------------------------------------------

def classify(
    mass,
    radius,
    teff,
    dnu,
    numax,
    emass=None,
    eradius=None,
    eteff=None,
    flame_flag=None,
    reference_model="reference",
):
    """
    Classify a star from its asteroseismic parameters.

    This function classifies the star independently using Δν and νmax
    and the selected reference evolutionary calibration. The other
    available calibrations and the propagated stellar-parameter
    uncertainties are evaluated to identify cases in which the
    classification is sensitive to the adopted model or input
    uncertainties.

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

    dnu : float
        Large frequency separation [μHz].

    numax : float
        Frequency of maximum oscillation power [μHz].

    reference_model : str, optional
        Calibration used for the nominal classification. Must be a key
        in BASTI_COEFFICIENTS. Defaults to "reference".

    Returns
    -------
    StellarClassification
        Complete evolutionary classification.

    """

    # ----------------------------------------------------------
    # Validate and apply the selected reference calibration
    # ----------------------------------------------------------

    if reference_model not in BASTI_COEFFICIENTS:
        available = ", ".join(BASTI_COEFFICIENTS)
        raise ValueError(
            f"Unknown reference_model {reference_model!r}. "
            f"Choose from: {available}."
        )

    dnu_stage = classify_parameter_model(
        dnu,
        mass,
        "dnu",
        model=reference_model,
    )

    numax_stage = classify_parameter_model(
        numax,
        mass,
        "numax",
        model=reference_model,
    )

    final_stage = combine_classifications(
        dnu_stage,
        numax_stage,
    )

    consistent = (
            dnu_stage == numax_stage
    )

    # ----------------------------------------------------------
    # Mass-offset diagnostic
    # ----------------------------------------------------------

    mass_offset_warning = (
        dnu_stage == "RGB"
        and numax_stage == "MS"
    )

    # ----------------------------------------------------------
    # Propagated seismic uncertainties
    # ----------------------------------------------------------

    if emass is not None and eradius is not None:
        sigma_dnu, sigma_numax = seismic_parameter_errors(
            mass=mass,
            radius=radius,
            teff=teff,
            emass=emass,
            eradius=eradius,
            eteff=eteff,
        )
    else:
        sigma_dnu, sigma_numax = None, None

    # ----------------------------------------------------------
    # Parameter-uncertainty classification test
    # ----------------------------------------------------------

    parameter_warnings = []

    if sigma_dnu is not None:

        dnu_2sigma = 2.0 * sigma_dnu

        dnu_minus = max(
            dnu - dnu_2sigma,
            0.0,
        )

        # Vary Δν only; keep νmax fixed.
        dnu_minus_stage = classify_parameter_model(
            dnu_minus,
            mass,
            "dnu",
            model=reference_model,
        )

        dnu_plus_stage = classify_parameter_model(
            dnu + dnu_2sigma,
            mass,
            "dnu",
            model=reference_model,
        )

        dnu_minus_final = combine_classifications(
            dnu_minus_stage,
            numax_stage,
        )

        dnu_plus_final = combine_classifications(
            dnu_plus_stage,
            numax_stage,
        )

        if dnu_minus_final != final_stage:
            parameter_warnings.append(
                (
                    "Δν",
                    "-2σ",
                    dnu_minus_final,
                )
            )

        if dnu_plus_final != final_stage:
            parameter_warnings.append(
                (
                    "Δν",
                    "+2σ",
                    dnu_plus_final,
                )
            )

    if sigma_numax is not None:

        numax_2sigma = 2.0 * sigma_numax

        numax_minus = max(
            numax - numax_2sigma,
            0.0,
        )

        # Vary νmax only; keep Δν fixed.
        numax_minus_stage = classify_parameter_model(
            numax_minus,
            mass,
            "numax",
            model=reference_model,
        )

        numax_plus_stage = classify_parameter_model(
            numax + numax_2sigma,
            mass,
            "numax",
            model=reference_model,
        )

        numax_minus_final = combine_classifications(
            dnu_stage,
            numax_minus_stage,
        )

        numax_plus_final = combine_classifications(
            dnu_stage,
            numax_plus_stage,
        )

        if numax_minus_final != final_stage:
            parameter_warnings.append(
                (
                    "νmax",
                    "-2σ",
                    numax_minus_final,
                )
            )

        if numax_plus_final != final_stage:
            parameter_warnings.append(
                (
                    "νmax",
                    "+2σ",
                    numax_plus_final,
                )
            )

    # Classification with alternative calibrations

    alternative_models = [
        model_name
        for model_name in BASTI_COEFFICIENTS
        if model_name != reference_model
    ]

    model_warnings = []

    for model_name in alternative_models:

        alt_dnu_stage = classify_parameter_model(
            dnu,
            mass,
            "dnu",
            model=model_name,
        )

        alt_numax_stage = classify_parameter_model(
            numax,
            mass,
            "numax",
            model=model_name,
        )

        alt_final_stage = combine_classifications(
            alt_dnu_stage,
            alt_numax_stage,
        )

        if alt_final_stage != final_stage:
            model_warnings.append(
                (
                    model_name,
                    alt_final_stage,
                )
            )

    # ----------------------------------------------------------
    # Stellar mass calibration range
    # ----------------------------------------------------------

    mass_range_ok = (
            MIN_CALIBRATION_MASS
            <= mass
            <= MAX_CALIBRATION_MASS
    )

    # ----------------------------------------------------------
    # Gaia FLAME quality
    # ----------------------------------------------------------

    flame_quality_ok = None

    if flame_flag is not None:

        flame_flag = str(flame_flag).strip()

        flame_quality_ok = flame_flag in ("00", "01")

    return StellarClassification(

        # Input stellar parameters
        mass=mass,
        radius=radius,
        teff=teff,

        # Input uncertainties
        emass=emass,
        eradius=eradius,
        eteff=eteff,

        # FLAME flag and check
        flame_flag=flame_flag,
        flame_quality_ok=flame_quality_ok,

        # Derived seismic quantities
        dnu=dnu,
        numax=numax,
        sigma_dnu=sigma_dnu,
        sigma_numax=sigma_numax,

        # Individual classifications
        dnu_stage=dnu_stage,
        numax_stage=numax_stage,

        # Final classification
        stage=final_stage,
        is_consistent=consistent,

        # Model dependence
        model_warnings=tuple(model_warnings),

        # Parameter uncertainty
        parameter_warnings=tuple(parameter_warnings),

        # Mass-offset diagnostic
        mass_offset_warning=mass_offset_warning,

        # Mass range
        mass_range_ok=mass_range_ok,

        # Reference calibration
        reference_model=reference_model,
    )
