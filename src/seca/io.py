"""
Input/output routines for SECA.

This module provides utilities to read stellar catalogues,
write classification catalogues and summarize the results.

Pedro Figueira
"""

from pathlib import Path
import numpy as np
from datetime import datetime

from . import __version__

# ----------------------------------------------------------------------
# Catalogue header
# ----------------------------------------------------------------------

def _classification_header(prefix):
    """
    Return the complete SECA classification catalogue header.

    Parameters
    ----------
    prefix : str
        Column(s) appearing before the stellar parameters.

    Returns
    -------
    str
        Complete self-documenting header.
    """

    return (
        f"# {prefix}"
        "Mass Radius Teff "
        "DeltaNu Numax "
        "SigmaDeltaNu SigmaNumax "
        "DeltaNuStage NumaxStage Stage "
        "Consistent "
        "ModelWarnings "
        "ParameterWarnings "
        "MassRangeOK "
        "FLAMEFlag FLAMEQualityOK\n"

        "# Units:\n"
        "# Mass [Msun]\n"
        "# Radius [Rsun]\n"
        "# Teff [K]\n"
        "# DeltaNu [uHz]\n"
        "# Numax [uHz]\n"
        "# SigmaDeltaNu [uHz]\n"
        "# SigmaNumax [uHz]\n"

        "# DeltaNuStage, NumaxStage : MS, SG, RGB\n"
        "# Stage : MS, MS-SG, SG, SG-RGB, RGB, NA\n"

        "# ModelWarnings : alternative BaSTI models giving a different classification\n"
        "# ParameterWarnings : propagated 2sigma seismic-parameter perturbations giving a different classification\n"

        "# MassRangeOK : 1=within calibrated mass range, 0=outside\n"
        "# FLAMEFlag : Gaia DR3 FLAME quality flag\n"
        "# FLAMEQualityOK : 1=yes, 0=no, NA=not applicable\n"
        "#\n"
    )

def _format_model_warnings(model_warnings):
    """
    Convert model-dependence warnings into a compact catalogue string.
    """

    if not model_warnings:
        return "NA"

    return ";".join(
        f"{model}:{stage}"
        for model, stage in model_warnings
    )

def _format_parameter_warnings(parameter_warnings):
    """
    Convert parameter-uncertainty warnings into a compact catalogue string.
    """

    if not parameter_warnings:
        return "NA"

    return ";".join(
        f"{quantity}:{direction}:{stage}"
        for quantity, direction, stage in parameter_warnings
    )

# ----------------------------------------------------------------------
# Read catalogue
# ----------------------------------------------------------------------

def read_catalog(filename):
    """
    Read an ASCII stellar or identifier catalogue.

    The input is interpreted according to the number of columns:

    - 1 column: Gaia DR3 or SIMBAD identifiers;
    - 3 columns: M, R, Teff;
    - 6 columns: M, R, Teff, eM, eR, eTeff.

    Parameters
    ----------
    filename : str
        Input catalogue.

    Returns
    -------
    catalog : dict or list
        Stellar parameters or identifiers.

    catalog_type : str
        One of ``"stellar"``, ``"gaia"``, or ``"simbad"``.
    """

    filename = Path(filename)

    try:

        with open(filename, "r") as f:

            lines = [
                line.strip()
                for line in f
                if line.strip()
                and not line.lstrip().startswith("#")
            ]

    except Exception as e:

        raise RuntimeError(
            f"Could not read catalogue '{filename}'."
        ) from e

    if not lines:

        raise RuntimeError(
            f"Input catalogue '{filename}' is empty."
        )

    # --------------------------------------------------------------
    # Determine catalogue type
    # --------------------------------------------------------------

    tokens = lines[0].split()

    # A one-token line is always an identifier catalogue.
    if len(tokens) == 1:
        return read_identifiers(filename)

    # --------------------------------------------------------------
    # Check whether this is a numerical stellar catalogue
    # --------------------------------------------------------------

    if len(tokens) in (3, 6):

        try:
            for token in tokens:
                float(token)

            is_numerical = True

        except ValueError:

            is_numerical = False

    else:

        is_numerical = False

    # --------------------------------------------------------------
    # Non-numerical multi-word lines are SIMBAD identifiers
    # --------------------------------------------------------------

    if not is_numerical:
        return read_identifiers(filename)

    ncol = len(tokens)

    try:

        data = np.loadtxt(
            filename,
            comments="#",
        )

    except Exception as e:

        raise RuntimeError(
            f"Could not read numerical catalogue "
            f"'{filename}'."
        ) from e

    if data.ndim == 1:
        data = data.reshape(1, -1)

    nstars = len(data)

    print(f"Found {nstars} star(s).")

    # --------------------------------------------------------------
    # Stellar parameters
    # --------------------------------------------------------------

    catalog = {
        "mass": data[:, 0],
        "radius": data[:, 1],
        "teff": data[:, 2],
    }

    if ncol == 3:

        print("Detected columns:")
        print("  M  R  Teff")
        print("Parameter precision check: not provided\n")

    else:

        print("Detected columns:")
        print("  M  R  Teff  eM  eR  eTeff")
        print("Parameter precision check: provided\n")

        catalog.update({
            "emass": data[:, 3],
            "eradius": data[:, 4],
            "eteff": data[:, 5],
        })

    return catalog, "stellar"
    
# ----------------------------------------------------------------------
# Read identifier file
# ----------------------------------------------------------------------

def read_identifiers(filename):
    """
    Read a one-column file containing Gaia DR3 or SIMBAD identifiers.

    Purely numerical identifiers are interpreted as Gaia DR3
    source identifiers. Non-numerical identifiers are interpreted
    as SIMBAD identifiers. A mixture of the two is rejected.

    Parameters
    ----------
    filename : str
        Input identifier file.

    Returns
    -------
    identifiers : list
        List of identifiers.

    identifier_type : str
        Either ``"gaia"`` or ``"simbad"``.
    """

    filename = Path(filename)

    print(f"Reading identifier file: {filename}")

    try:

        with open(filename, "r") as f:

            identifiers = [
                line.strip()
                for line in f
                if line.strip()
                and not line.lstrip().startswith("#")
            ]

    except Exception as e:

        raise RuntimeError(
            f"Could not read identifier file '{filename}'."
        ) from e

    if not identifiers:

        raise RuntimeError(
            f"Identifier file '{filename}' is empty."
        )

    # --------------------------------------------------------------
    # Determine identifier type
    # --------------------------------------------------------------

    is_numeric = [
        identifier.isdigit()
        for identifier in identifiers
    ]

    if all(is_numeric):

        identifier_type = "gaia"

    elif not any(is_numeric):

        identifier_type = "simbad"

    else:

        raise RuntimeError(
            "Identifier file contains a mixture of "
            "Gaia DR3 numerical identifiers and "
            "SIMBAD identifiers. "
            "All identifiers must be of the same type."
        )

    print(f"Found {len(identifiers)} identifier(s).")

    if identifier_type == "gaia":

        print("Detected identifier type: Gaia DR3 source_id")

    else:

        print("Detected identifier type: SIMBAD identifier")

    print()

    return identifiers, identifier_type


# ----------------------------------------------------------------------
# Write catalogue
# ----------------------------------------------------------------------

def write_catalog(filename, results):
    """
    Write a SECA classification catalogue.

    Parameters
    ----------
    filename : str

    results : list(StellarClassification)
    """

    input_file = Path(filename)

    output_file = input_file.with_name(
        input_file.stem + "_seca" + input_file.suffix
    )

    with open(output_file, "w") as f:

        # ==========================================================
        # Header
        # ==========================================================

        f.write(
            _classification_header("")
        )

        # ==========================================================
        # Write data
        # ==========================================================

        for r in results:
            f.write(
                f"{r.mass:.5f} "
                f"{r.radius:.5f} "
                f"{r.teff:.1f} "

                f"{r.dnu:.3f} "
                f"{r.numax:.3f} "

                f"{'NA' if r.sigma_dnu is None else f'{r.sigma_dnu:.3f}'} "
                f"{'NA' if r.sigma_numax is None else f'{r.sigma_numax:.3f}'} "

                f"{r.dnu_stage} "
                f"{r.numax_stage} "
                f"{r.stage if r.stage is not None else 'NA'} "
                f"{int(r.is_consistent)} "

                f"{_format_model_warnings(r.model_warnings)} "
                f"{_format_parameter_warnings(r.parameter_warnings)} "

                f"{int(r.mass_range_ok)} "
                f"{r.flame_flag if r.flame_flag is not None else 'NA'} "
                f"{'NA' if r.flame_quality_ok is None else int(r.flame_quality_ok)}\n"
            )

    print(f"\nCatalogue written to {output_file}")

    return output_file

# ----------------------------------------------------------------------
# Write identifier catalogue
# ----------------------------------------------------------------------

def write_identifier_catalog(
    filename,
    identifiers,
    results,
    catalog_type,
    source_ids=None,
):
    """
    Write SECA classifications for a Gaia/SIMBAD identifier catalogue.

    Parameters
    ----------
    filename : str
        Input identifier catalogue.

    identifiers : list
        Original identifiers.

    results : list(StellarClassification)
        Classification results.

    catalog_type : str
        Either ``"gaia"`` or ``"simbad"``.

    source_ids : list, optional
        Resolved Gaia DR3 source IDs. Required for SIMBAD input.
    """

    input_file = Path(filename)

    output_file = input_file.with_name(input_file.stem + "_seca" + input_file.suffix)

    if len(identifiers) != len(results):
        raise ValueError("Number of identifiers and classification results must be identical.")

    if catalog_type == "simbad":

        if source_ids is None:
            raise ValueError(
                "source_ids must be provided for SIMBAD catalogues."
            )

        if len(source_ids) != len(results):
            raise ValueError("Number of Gaia source IDs and classification results must be identical.")

    with open(output_file, "w") as f:

        # ==============================================================
        # Header
        # ==============================================================

        if catalog_type == "gaia":

            f.write(
                _classification_header(
                    "Gaia_source_id "
                )
            )

        else:

            f.write(
                _classification_header(
                    "Identifier Gaia_source_id "
                )
            )

        # ==============================================================
        # Data
        # ==============================================================

        for i, r in enumerate(results):

            if catalog_type == "gaia":

                prefix = (f"{int(identifiers[i])} ")

            else:

                prefix = (
                    f"{identifiers[i]} "
                    f"{int(source_ids[i])} "
                )

            f.write(
                prefix

                + f"{r.mass:.5f} "
                + f"{r.radius:.5f} "
                + f"{r.teff:.1f} "

                + f"{r.dnu:.3f} "
                + f"{r.numax:.3f} "

                + f"{'NA' if r.sigma_dnu is None else f'{r.sigma_dnu:.3f}'} "
                + f"{'NA' if r.sigma_numax is None else f'{r.sigma_numax:.3f}'} "

                + f"{r.dnu_stage} "
                + f"{r.numax_stage} "
                + f"{r.stage if r.stage is not None else 'NA'} "
                + f"{int(r.is_consistent)} "

                + f"{_format_model_warnings(r.model_warnings)} "
                + f"{_format_parameter_warnings(r.parameter_warnings)} "

                + f"{int(r.mass_range_ok)} "
                + f"{r.flame_flag if r.flame_flag is not None else 'NA'} "
                + f"{'NA' if r.flame_quality_ok is None else int(r.flame_quality_ok)}\n"
            )

    print(f"\nClassification catalogue written to {output_file}")

    return output_file

# ----------------------------------------------------------------------
# Print one result
# ----------------------------------------------------------------------

def print_result(result):
    """
    Print one classification.
    """

    print(result)

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------

def _summary_text(results):
    """
    Generate a text summary of the classifications.

    Parameters
    ----------
    results : list(StellarClassification)

    Returns
    -------
    str
        Formatted summary.
    """

    stages = [
        "MS",
        "MS-SG",
        "SG",
        "SG-RGB",
        "RGB",
    ]

    lines = []

    lines.append("")
    lines.append("=" * 50)
    lines.append("Summary")
    lines.append("=" * 50)

    nstars = len(results)

    lines.append(f"Total stars : {nstars}")
    lines.append("")

    # ----------------------------------------------------------
    # Evolutionary classes
    # ----------------------------------------------------------

    lines.append("Evolutionary classes")

    for stage in stages:

        n = sum(r.stage == stage for r in results)
        lines.append(f"  {stage:13s}: {n:6d}")

    # ----------------------------------------------------------
    # Consistency
    # ----------------------------------------------------------

    nconsistent = sum(r.is_consistent for r in results)

    lines.append("")

    lines.append(
        f"Consistent classifications   : "
        f"{nconsistent}/{nstars}"
    )

    ninconsistent = sum(not r.is_consistent for r in results)

    lines.append("")

    lines.append(
        f"Inconsistent classifications : "
        f"{ninconsistent}/{nstars}"
    )

    # ----------------------------------------------------------
    # Model dependence
    # ----------------------------------------------------------

    n_model_dependent = sum(
        bool(r.model_warnings)
        for r in results
    )

    lines.append("")

    lines.append(
        f"Model-dependent classifications : "
        f"{n_model_dependent}/{nstars}"
    )

    # ----------------------------------------------------------
    # Parameter uncertainty
    # ----------------------------------------------------------

    n_parameter_sensitive = sum(
        bool(r.parameter_warnings)
        for r in results
    )

    lines.append("")

    lines.append(
        f"Parameter-uncertainty warnings : "
        f"{n_parameter_sensitive}/{nstars}"
    )

    return "\n".join(lines)


# ----------------------------------------------------------------------
# Print summary
# ----------------------------------------------------------------------

def print_summary(results):
    """
    Print a summary of the classifications.
    """

    print(_summary_text(results))


# ----------------------------------------------------------------------
# Write classification summary
# ----------------------------------------------------------------------

def write_summary(filename, results):
    """
    Write a summary of the classifications to a text file.

    Parameters
    ----------
    filename : str
        Input catalogue filename.

    results : list(StellarClassification)
        Classification results.

    Returns
    -------
    output_file : pathlib.Path
        Path to the summary file.
    """

    input_file = Path(filename)

    output_file = input_file.with_name(input_file.stem + "_classification.txt")

    with open(output_file, "w") as f:

        f.write("SECA Stellar Classification Summary\n")
        f.write(f"Generated by SECA v{__version__}\n")

        f.write(
            f"Created : "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        f.write(f"Input file : {input_file.name}\n")

        f.write(_summary_text(results))
        f.write("\n")

    print(f"Summary written to {output_file}")

    return output_file