# ITDCarry

ITDCarry is a non-clinical computational proof of concept. It challenges a later
pipeline with a previously known FLT3-ITD embedded in disclosed synthetic reads
and records whether that exact marker is recoverable under the tested conditions.

It does **not** determine disease status, MRD, remission, relapse, or treatment.

## Status

The project is being built from the scientific core outward. The initial fixture
is getITD's attributed upstream test dataset; a custom synthetic fixture must not
be presented as validated until its manifest and real caller output are frozen.

## Verdicts

- `COMPUTATIONALLY_OBSERVABLE`: a completed challenge recovered the exact marker.
- `NOT_TECHNICALLY_COMPARABLE`: a completed challenge did not recover it.
- `NO_CONCLUSION`: execution, parsing, or provenance computation was incomplete.

## Local checks

```powershell
.\.venv\Scripts\python.exe -m pytest
```

