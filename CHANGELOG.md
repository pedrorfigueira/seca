# Changelog

## v1.0.0 — 2026-08-29

- First release version

## v1.1.0 — 2026-10-09

### Added
- Propagated uncertainties from the solar reference values in the asteroseismic scaling relations.
- Diagnostic warning for stars classified as MS by nu_max and RGB by Delta nu, potentially indicating a positive offset in the input stellar mass.
- Option to select the reference transition-frequency calibration.

### Changed
- Moved the seismic-parameter uncertainty calculations to `scaling.py`.
