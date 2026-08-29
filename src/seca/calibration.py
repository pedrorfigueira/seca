"""
Calibration constants and polynomial coefficients for SECA.

The transition frequencies are described by cubic polynomials of the form

    y(M) = a3*M**3 + a2*M**2 + a1*M + a0

where M is the stellar mass in solar masses and y is either Δν (μHz)
or νmax (μHz).

The adopted calibration is based on BaSTI evolutionary tracks
(Hidalgo et al. 2018). The individual model variants are retained
below so that the transition zones can be defined from the envelope
of the model predictions.

The two transition zones are:

    MS-SG
    SG-RGB

The ordered evolutionary sequence used by SECA is:

    MS -> MS-SG -> SG -> SG-RGB -> RGB
"""

# ----------------------------------------------------------------------
# Solar reference values
# ----------------------------------------------------------------------

DNU_SUN = 135.1          # μHz
NUMAX_SUN = 3090.0       # μHz
TEFF_SUN = 5772.0        # K

# ----------------------------------------------------------------------
# Stellar mass calibration range
# ----------------------------------------------------------------------

MIN_CALIBRATION_MASS = 1.0
MAX_CALIBRATION_MASS = 2.0

# ----------------------------------------------------------------------
# BaSTI calibration coefficients
#
# Each model provides the two evolutionary boundaries:
#
#     MS-SG
#     SG-RGB
#
# The coefficients correspond to:
#
#     y(M) = a3*M**3 + a2*M**2 + a1*M + a0
#
# where M is in Msun and y is in μHz.
# ----------------------------------------------------------------------

BASTI_COEFFICIENTS = {

    "reference": {

        "feh": 0.06,

        "MS-SG": {

            "dnu": (
                -2.953e+01,
                 1.953e+02,
                -4.389e+02,
                 3.532e+02,
            ),

            "numax": (
                -9.138e+02,
                 5.547e+03,
                -1.150e+04,
                 8.405e+03,
            ),
        },

        "SG-RGB": {

            "dnu": (
                 3.415e+01,
                -1.536e+02,
                 1.953e+02,
                -3.239e+01,
            ),

            "numax": (
                 8.037e+02,
                -3.656e+03,
                 4.863e+03,
                -1.279e+03,
            ),
        },
    },


    "no_diffusion": {

        "feh": 0.06,

        "MS-SG": {

            "dnu": (
                 1.536e+01,
                -2.922e+01,
                -6.843e+01,
                 1.521e+02,
            ),

            "numax": (
                 1.904e+02,
                 4.060e+01,
                -2.441e+03,
                 3.505e+03,
            ),
        },

        "SG-RGB": {

            "dnu": (
                 2.030e+01,
                -8.472e+01,
                 8.271e+01,
                 2.739e+01,
            ),

            "numax": (
                 4.997e+02,
                -2.148e+03,
                 2.411e+03,
                 1.739e+01,
            ),
        },
    },


    "no_overshooting": {

        "feh": 0.06,

        "MS-SG": {

            "dnu": (
                -3.687e+01,
                 2.101e+02,
                -4.107e+02,
                 3.069e+02,
            ),

            "numax": (
                -8.671e+02,
                 4.846e+03,
                -9.274e+03,
                 6.580e+03,
            ),
        },

        "SG-RGB": {

            "dnu": (
                -3.282e+00,
                 1.783e+01,
                -5.490e+01,
                 8.587e+01,
            ),

            "numax": (
                -3.993e+01,
                 1.894e+02,
                -7.227e+02,
                 1.350e+03,
            ),
        },
    },


    "metal_minus30": {

        "feh": -0.30,

        "MS-SG": {

            "dnu": (
                -6.187e+01,
                 3.428e+02,
                -6.434e+02,
                 4.328e+02,
            ),

            "numax": (
                -1.462e+03,
                 7.908e+03,
                -1.444e+04,
                 9.258e+03,
            ),
        },

        "SG-RGB": {

            "dnu": (
                 4.745e+00,
                -7.622e+00,
                -4.005e+01,
                 8.589e+01,
            ),

            "numax": (
                 1.390e+02,
                -3.827e+02,
                -3.405e+02,
                 1.283e+03,
            ),
        },
    },


    "metal_plus30": {

        "feh": +0.30,

        "MS-SG": {

            "dnu": (
                -7.563e+01,
                 4.195e+02,
                -8.031e+02,
                 5.534e+02,
            ),

            "numax": (
                -2.179e+03,
                 1.177e+04,
                -2.171e+04,
                 1.406e+04,
            ),
        },

        "SG-RGB": {

            "dnu": (
                 1.967e+01,
                -8.145e+01,
                 7.346e+01,
                 3.996e+01,
            ),

            "numax": (
                 5.168e+02,
                -2.208e+03,
                 2.369e+03,
                 2.497e+02,
            ),
        },
    },
}
