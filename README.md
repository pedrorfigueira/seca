# SECA

**SECA** (Stellar Evolutionary Classification with Asteroseismology) is a lightweight Python package for classifying stars into the main sequence (MS), subgiant (SG), red giant branch (RGB), or the transition regions between these evolutionary stages using asteroseismic scaling relations.

The method is described in

> Figueira, Cunha and Luque (2026), *Direct classification of stellar evolutionary stages from fundamental stellar parameters*, Astronomy & Astrophysics (submitted).

SECA requires only the stellar mass, radius and effective temperature. It computes the asteroseismic quantities

- large frequency separation ($\Delta\nu$),
- frequency of maximum oscillation power ($\nu_{\rm max}$),

using standard scaling relations, and applies mass-dependent transition frequencies calibrated on BaSTI evolutionary models.

The reference BaSTI model provides the authoritative classification. Alternative BaSTI model variants are evaluated separately to identify classifications that are sensitive to the adopted stellar-evolution physics.

When stellar-parameter uncertainties are provided, SECA propagates them to $\Delta\nu$ and $\nu_{\rm max}$ and checks whether the final classification changes within the corresponding $2\sigma$ uncertainty range.

SECA can also retrieve stellar parameters directly from Gaia DR3, either from a Gaia source identifier or from a SIMBAD identifier.

---

# Installation

SECA requires **Python ≥ 3.9**.

Clone the repository:

```bash
git clone https://github.com/pedrofigueira/seca.git
cd seca
````

and install:

```bash
pip install .
```

For development:

```bash
pip install -e .
```

---

# Python usage

The main convenience interface is `classify_star()`, which computes the seismic parameters from the stellar mass, radius and effective temperature and performs the evolutionary classification.

For example:

```python
import seca

result = seca.classify_star(
    mass=1.35,
    radius=2.70,
    teff=5600,
)

print(result)
```

If mass and radius uncertainties are available, SECA propagates them to the seismic quantities $\Delta\nu$ and $\nu_{\rm max}$. An effective-temperature uncertainty can also be supplied and is included in the $\nu_{\rm max}$ uncertainty propagation.

```python
result = seca.classify_star(
    mass=1.35,
    radius=2.70,
    teff=5600,
    emass=0.04,
    eradius=0.08,
    eteff=50,
)
```
The returned `StellarClassification` object contains

* $\Delta\nu$,
* $\nu_{\rm max}$,
* propagated uncertainties on $\Delta\nu$ and $\nu_{\rm max}$ when input uncertainties are provided,
* individual $\Delta\nu$ and $\nu_{\rm max}$ classifications,
* final evolutionary classification,
* model-dependence warnings,
* parameter-uncertainty warnings,
* Gaia FLAME quality information when available,
* a consistency indicator.

---

# Command-line usage

The `seca` command provides several ways of supplying stellar parameters.

## Single star from stellar parameters

A single star can be classified directly from its mass, radius and effective temperature:

```bash
seca \
    -m 1.35 \
    -r 2.70 \
    -t 5600
```

The output includes the stellar parameters, seismic quantities, evolutionary classification and, when applicable, the quality assessment.

Uncertainties can be provided with:

```bash
seca \
    -m 1.35 \
    -r 2.70 \
    -t 5600 \
    --emass 0.04 \
    --eradius 0.08 \
    --eteff 50
````

Mass and radius uncertainties must be supplied together. The effective-temperature uncertainty is optional.

When uncertainties are provided, SECA reports the propagated uncertainties in $\Delta\nu$ and $\nu_{\rm max}$ and checks whether the final classification changes when either quantity is varied independently by $2\sigma$.

SECA also evaluates alternative BaSTI evolutionary models and reports cases where they lead to a different final classification.

---

# Gaia DR3 source

A star can be classified directly from its Gaia DR3 source identifier:

```bash
seca -g 123456789012345678
```

SECA queries Gaia DR3 for the stellar mass, radius and effective temperature and then performs the classification.

---

# SIMBAD identifier

A star can also be specified using a SIMBAD identifier:

```bash
seca -s "HD 127195"
```

SECA first resolves the SIMBAD identifier to a Gaia DR3 source identifier and then retrieves the corresponding Gaia DR3 stellar parameters.

The command therefore performs the following sequence:

```text
SIMBAD identifier
       ↓
Gaia DR3 source ID
       ↓
Gaia DR3 stellar parameters
       ↓
SECA classification
```

---

# Catalogue mode

SECA can classify an entire catalogue using the `-f` option.

```bash
seca -f stars.dat
```

The interpretation of the input file is automatic.

## Stellar-parameter catalogues

A numerical catalogue can contain three columns:

```text
M   R   Teff
```

or six columns:

```text
M   R   Teff   eM   eR   eTeff
```

with one star per line.

For example:

```text
1.10  1.20  5800
1.35  2.70  5600
1.50  3.10  5400
```

or, with uncertainties:

```text
1.10  1.20  5800  0.03  0.02  50
1.35  2.70  5600  0.04  0.08  50
1.50  3.10  5400  0.05  0.10  60
```

SECA automatically detects whether uncertainties are present and reports this interpretation to the user.

For example:

```text
Detected columns:
  M  R  Teff
Parameter uncertainties: not provided
````

or:

```text
Detected columns:
  M  R  Teff  eM  eR  eTeff
Parameter uncertainties: provided
```

The resulting catalogue is written automatically with `_seca` appended to the input filename. 

It contains the input stellar parameters, the derived seismic quantities and their propagated uncertainties, the individual and final classifications, the consistency indicator, model-dependence warnings, parameter-uncertainty warnings, the calibration-range status and, for Gaia-derived inputs, the FLAME quality information.

---

# Identifier catalogues

The same `-f` option can also be used with a file containing **one identifier per line**.

For example, a Gaia DR3 identifier catalogue:

```text
123456789012345678
234567890123456789
345678901234567890
```

can be processed with:

```bash
seca -f gaia_ids.txt
```

Because all identifiers are numerical, SECA automatically interprets the file as a Gaia DR3 source-ID catalogue.

Similarly, a SIMBAD identifier catalogue can contain entries such as:

```text
HD 127195
18 Sco
HD 102870
```

and can be processed with:

```bash
seca -f simbad_ids.txt
```

Because the identifiers are non-numerical, SECA automatically interprets the file as a SIMBAD identifier catalogue.

The program explicitly reports its interpretation, for example:

```text
Input interpreted as a Gaia DR3 identifier catalogue.
```

or:

```text
Input interpreted as a SIMBAD identifier catalogue.
```

For Gaia-derived catalogues, SECA also retrieves the Gaia DR3 `flags_flame` value for each source and reports whether it satisfies the recommended `00` or `01` quality criterion.


A single identifier catalogue cannot contain both Gaia source IDs and SIMBAD identifiers.  SECA will detect the mixture and stop with an error.

---

# Catalogue output

For stellar-parameter catalogues, SECA produces a self-documenting output catalogue. For example:

```text
stars.dat
```

generates:

```text
stars_seca.dat
```

The output header documents the columns, units and warning conventions used by SECA.

For identifier catalogues, SECA also writes two text files:

* `_seca.txt` contains the detailed SECA output for each object.
* `_classification.txt` contains the classification summary.

---

# Parameter uncertainties

When mass and radius uncertainties are provided, SECA propagates them through the standard asteroseismic scaling relations to estimate uncertainties on $\Delta\nu$ and $\nu_{\rm max}$. An effective-temperature uncertainty is included in the $\nu_{\rm max}$ propagation when available.

The propagated uncertainties are then used to test the robustness of the reference classification. The $\Delta\nu$ and $\nu_{\rm max}$ values are varied independently by $\pm2\sigma$, and the resulting classifications are compared with the reference classification.

If either perturbation changes the final classification, SECA issues a parameter-uncertainty warning. The reference classification is retained.

Possible cross-effects between stellar-parameter uncertainties and changes in evolutionary model physics are not included in this test; model dependence is evaluated separately.

---

# Model dependence

SECA uses a reference BaSTI evolutionary calibration for the authoritative classification.

Alternative BaSTI model variants are evaluated independently. If an alternative model produces a different final classification, SECA reports the model and the alternative classification through `model_warnings`.

The reference BaSTI classification is always retained.

---

# Gaia FLAME quality

For stellar parameters retrieved from Gaia DR3, SECA checks the `flags_flame` quality flag. The recommended values are `00` and `01`.

The FLAME flag is reported together with the classification. It does not alter the reference SECA classification.

---

# Command-line summary

| Option            | Description                                      |
| ----------------- | ------------------------------------------------ |
| `-m MASS`         | Stellar mass [$M_\odot$]                         |
| `-r RADIUS`       | Stellar radius [$R_\odot$]                       |
| `-t TEFF`         | Effective temperature [K]                        |
| `-f FILE`         | Stellar-parameter or identifier catalogue        |
| `-g SOURCE_ID`    | Gaia DR3 source identifier                       |
| `-s IDENTIFIER`   | SIMBAD identifier                                |
| `--emass VALUE`   | Mass uncertainty [$M_\odot$]                     |
| `--eradius VALUE` | Radius uncertainty [$R_\odot$]                   |
| `--eteff VALUE`   | Effective-temperature uncertainty [K]            |
| `--version`       | Display SECA version                             |

The input modes `-f`, `-g` and `-s` are mutually exclusive. Individual stellar parameters cannot be combined with these input modes.

---

# Package structure

```text
seca/
├── calibration.py      # constants and calibration coefficients
├── scaling.py          # asteroseismic scaling relations
├── classification.py   # classification rules and output class
├── core.py             # high-level classification interface
├── io.py               # catalogue and identifier I/O
├── gaia.py             # Gaia DR3 interface
├── simbad.py           # SIMBAD identifier resolution
├── config.py           # configuration
└── cli.py              # command-line interface
```

---

# Citation

If you use SECA in published work, please cite

> Figueira, Cunha and Luque (2026), *Direct classification of stellar evolutionary stages from fundamental stellar parameters*, A&A.

---

# Acknowledgements

Pedro Figueira acknowledges financial support from the Severo Ochoa grant CEX2021-001131-S funded by MCIN/AEI/10.13039/501100011033. Pedro Figueira is also funded by the European Union (ERC, THIRSTEE, 101164189). Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Research Council. Neither the European Union nor the granting authority can be held responsible for them.

SECA depends on the open-source scientific Python ecosystem, in particular NumPy. We gratefully acknowledge the developers and maintainers of these community projects.
