# ITDCarry judge notes

## The 20-second explanation

ITDCarry tests whether a changed computational pipeline can still recover an
exact previously known FLT3-ITD from disclosed synthetic reads. It prevents a
pipeline miss from being silently presented as a technically comparable
longitudinal negative.

## What is real

- Deterministic paired FASTQ fixture: 200 fragments, 251 bp, 60% intended VAF.
- getITD 1.5.17 at commit `d5b80410bdf8dfe00474cd8b51fdf27c5ba0911b`.
- getITD executes inside a Daytona sandbox and produces the parsed TSV.
- Position, length, and sequence are matched exactly without an LLM.
- Neo4j writes provenance and returns the verdict through a scoped Cypher query.
- Twenty-three automated tests and GitHub Actions CI pass.

## Live demonstration

1. Show the known 21-bp marker.
2. Click **Verify technical comparability**.
3. Point out the real Daytona sandbox ID and configuration fingerprints.
4. Compatible profile: exact recovery.
5. Changed profile: completed without exact recovery.
6. Neo4j verdict: `NOT_TECHNICALLY_COMPARABLE`.

## Safety boundary

This synthetic proof of concept evaluates software behavior only. It does not
determine leukemia, MRD, remission, relapse, or treatment, and it does not
validate specimen collection, extraction, library preparation, or sequencing.
