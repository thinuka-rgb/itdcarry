# Two-minute demo

**0:00–0:20 — Problem**

“When a known AML mutation disappears from a later report, biology may have
changed, but the computational pipeline may also have changed. Before interpreting
absence, we first ask whether the later pipeline can recover that exact marker.”

**0:20–0:40 — Case**

“This fictional case records one 21-base FLT3-ITD. Follow-up says ‘not detected,’
and its caller filter changed.”

**0:40–1:15 — Run**

Press **Run observability challenge**.

“ITDCarry sends the same deterministic synthetic FASTQ fixture through two pinned
getITD profiles inside one Daytona sandbox. Matching uses position, length, and
sequence—not an LLM.”

**1:15–1:45 — Evidence**

“Compatible profile recovers exact marker. Changed profile completes, but its
five-unique-read requirement rejects a marker supported by four unique reads.
Fixture hash stays identical; configuration hashes differ.”

**1:45–2:00 — Verdict and boundary**

“Neo4j links case, marker, pipeline, challenge, and result. It returns ‘not
technically comparable’ for this changed pipeline. This says nothing about
patient biology or clinical status.”

## Failure line

“Live service is unavailable, so we are showing a retained, timestamped real run.
ITDCarry reports no conclusion when execution or provenance is incomplete.”

