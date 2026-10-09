#!/usr/bin/env python3
"""
Command-line interface for SECA.

Pedro Figueira
"""

import argparse
import sys

from . import __version__

from .core import classify_star, classify_catalog
from .calibration import BASTI_COEFFICIENTS

from .io import (
    read_catalog,
    write_catalog,
    write_identifier_catalog,
    write_summary,
    print_result,
    print_summary,
)

from .gaia import get_gaia_parameters
from .simbad import get_gaia_source_id

# ----------------------------------------------------------------------
# Parser
# ----------------------------------------------------------------------

def build_parser():

    parser = argparse.ArgumentParser(
        prog="seca",
        description="Stellar Evolutionary Classification with Asteroseismology",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"SECA {__version__}",
    )

    # --------------------------------------------------------------
    # Catalogue / Gaia / SIMBAD modes
    # --------------------------------------------------------------

    input_group = parser.add_mutually_exclusive_group()

    input_group.add_argument(
        "-f",
        "--file",
        type=str,
        help="Input catalogue or identifier file (ASCII).",
    )

    input_group.add_argument(
        "-g",
        "--gaia",
        type=int,
        metavar="SOURCE_ID",
        help="Gaia DR3 source identifier.",
    )

    input_group.add_argument(
        "-s",
        "--simbad",
        type=str,
        metavar="IDENTIFIER",
        help="SIMBAD identifier used to resolve a Gaia DR3 source.",
    )

    # --------------------------------------------------------------
    # Single-star mode
    # --------------------------------------------------------------

    parser.add_argument(
        "-m",
        "--mass",
        type=float,
        help="Stellar mass [Msun].",
    )

    parser.add_argument(
        "-r",
        "--radius",
        type=float,
        help="Stellar radius [Rsun].",
    )

    parser.add_argument(
        "-t",
        "--teff",
        type=float,
        help="Effective temperature [K].",
    )

    # --------------------------------------------------------------
    # Reference calibration
    # --------------------------------------------------------------

    parser.add_argument(
        "--reference-model",
        choices=tuple(BASTI_COEFFICIENTS),
        default="reference",
        metavar="MODEL",
        help=(
            "BaSTI calibration used as the reference for classification "
            "(default: reference)."
        ),
    )

    # --------------------------------------------------------------
    # Stellar parameter uncertainties
    # --------------------------------------------------------------

    parser.add_argument(
        "--emass",
        type=float,
        help="Mass uncertainty [Msun]. Used with --eradius for precision check.",
    )

    parser.add_argument(
        "--eradius",
        type=float,
        help="Radius uncertainty [Rsun]. Used with --emass for precision check.",
    )

    parser.add_argument(
        "--eteff",
        type=float,
        help="Effective temperature uncertainty [K]. Optional.",
    )

    return parser


# ----------------------------------------------------------------------
# Gaia classification helper
# ----------------------------------------------------------------------

def classify_gaia_source(source_id, reference_model="reference"):
    """
    Retrieve Gaia DR3 stellar parameters and classify the star.
    """

    stellar_parameters = get_gaia_parameters(source_id)

    print(
        f"Gaia DR3 source : "
        f"{stellar_parameters['source_id']}"
    )

    print()

    result = classify_star(
        mass=stellar_parameters["mass"],
        radius=stellar_parameters["radius"],
        teff=stellar_parameters["teff"],

        emass=stellar_parameters.get("emass"),
        eradius=stellar_parameters.get("eradius"),
        eteff=stellar_parameters.get("eteff"),

        flame_flag=stellar_parameters.get("flame_flag"),
        reference_model=reference_model,
    )

    print_result(result)

    return result


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():

    parser = build_parser()
    args = parser.parse_args()

    print()
    print(f"SECA {__version__}")
    print("Stellar Evolutionary Classification with Asteroseismology")
    print("---------------------------------------------------------\n")

    try:

        # --------------------------------------------------------------
        # Gaia / simbad / catalogue modes cannot use individual params
        # --------------------------------------------------------------

        if (
            args.file is not None
            or args.gaia is not None
            or args.simbad is not None
        ):
            if any(
                x is not None
                for x in (
                    args.mass,
                    args.radius,
                    args.teff,
                    args.emass,
                    args.eradius,
                    args.eteff,
                )
            ):
                parser.error(
                    "Do not combine -f/--file, -g/--gaia, or "
                    "-s/--simbad with individual stellar parameters."
                )

        # --------------------------------------------------------------
        # Check stellar-parameter uncertainties
        # --------------------------------------------------------------

        # Mass and radius uncertainties are required together.
        if (args.emass is None) != (args.eradius is None):

            parser.error("Either provide both --emass and --eradius or neither.")

        # --------------------------------------------------------------
        # SIMBAD mode
        # --------------------------------------------------------------

        if args.simbad is not None:

            gaia_source_id = get_gaia_source_id(args.simbad)
            print(f"SIMBAD identifier : {args.simbad}")
            classify_gaia_source(gaia_source_id, args.reference_model)

            return

        # --------------------------------------------------------------
        # Gaia DR3 mode
        # --------------------------------------------------------------

        if args.gaia is not None:

            classify_gaia_source(args.gaia, args.reference_model)

            return

        # --------------------------------------------------------------
        # Catalogue mode
        # --------------------------------------------------------------

        if args.file is not None:

            catalog, catalog_type = read_catalog(args.file)

            # Stellar-parameter catalogue

            if catalog_type == "stellar":

                results = classify_catalog(**catalog, reference_model=args.reference_model)

                write_catalog(args.file, results)
                print_summary(results)
                write_summary(args.file, results)

                return

            # --------------------------------------------------------------
            # Identifier catalogue
            # --------------------------------------------------------------

            n_skipped = 0

            if catalog_type in ("gaia", "simbad"):

                identifiers = catalog
                results = []
                source_ids = []
                successful_identifiers = []

                if catalog_type == "gaia":

                    print("Input interpreted as a Gaia DR3 identifier catalogue.")

                    for identifier in identifiers:

                        print("----------------------------------------")
                        print(f"Gaia DR3 source : {identifier}")

                        try:

                            result = classify_gaia_source(int(identifier), args.reference_model)
                            results.append(result)
                            successful_identifiers.append(identifier)

                        except RuntimeError as exc:

                            n_skipped += 1
                            print(f"SECA warning: {exc}")
                            print(f"Skipping Gaia source {identifier}.")
                            print()

                            continue

                else:

                    print("Input interpreted as a SIMBAD identifier catalogue.")

                    for identifier in identifiers:

                        print("----------------------------------------")
                        print(f"SIMBAD identifier : {identifier}")

                        try:

                            gaia_source_id = get_gaia_source_id(identifier)

                            result = classify_gaia_source(gaia_source_id, args.reference_model)
                            results.append(result)
                            successful_identifiers.append(identifier)
                            source_ids.append(gaia_source_id)

                        except RuntimeError as exc:

                            n_skipped += 1
                            print(f"SECA warning: {exc}")
                            print(f"Skipping {identifier}.")
                            print()

                            continue

                # ----------------------------------------------------------
                # Write full classification catalogue
                # ----------------------------------------------------------

                write_identifier_catalog(
                    args.file,
                    successful_identifiers,
                    results,
                    catalog_type,
                    source_ids=(
                        source_ids
                        if catalog_type == "simbad"
                        else None
                    ),
                )

                # ----------------------------------------------------------
                # Print and write summary
                # ----------------------------------------------------------

                print_summary(results)

                write_summary(args.file, results)

                print(f"\nSuccessfully classified : {len(results)}")
                print(f"Skipped                  : {n_skipped}")

                return

            parser.error(f"Unknown catalogue type: {catalog_type}")

        # --------------------------------------------------------------
        # Single-star mode
        # --------------------------------------------------------------

        if None in (args.mass, args.radius, args.teff):

            parser.error(
                "Provide either -s IDENTIFIER, "
                "-g SOURCE_ID, -f FILE, or all of "
                "-m MASS -r RADIUS -t TEFF."
            )

        result = classify_star(

            mass=args.mass,
            radius=args.radius,
            teff=args.teff,

            emass=args.emass,
            eradius=args.eradius,
            eteff=args.eteff,
            reference_model=args.reference_model,

        )

        print_result(result)

    except RuntimeError as exc:

        print(
            f"SECA error: {exc}",
            file=sys.stderr,
        )

        return 1


# ----------------------------------------------------------------------

if __name__ == "__main__":

    main()
