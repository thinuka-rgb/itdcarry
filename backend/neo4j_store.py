from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from neo4j import GraphDatabase
import truststore

from backend.domain import Verdict


CONSTRAINTS = (
    "CREATE CONSTRAINT case_id_unique IF NOT EXISTS FOR (n:Case) REQUIRE n.case_id IS UNIQUE",
    "CREATE CONSTRAINT variant_id_unique IF NOT EXISTS FOR (n:ITD) REQUIRE n.variant_id IS UNIQUE",
    "CREATE CONSTRAINT followup_id_unique IF NOT EXISTS FOR (n:FollowUp) REQUIRE n.followup_id IS UNIQUE",
    "CREATE CONSTRAINT pipeline_id_unique IF NOT EXISTS FOR (n:Pipeline) REQUIRE n.pipeline_id IS UNIQUE",
    "CREATE CONSTRAINT challenge_id_unique IF NOT EXISTS FOR (n:Challenge) REQUIRE n.challenge_id IS UNIQUE",
    "CREATE CONSTRAINT result_id_unique IF NOT EXISTS FOR (n:Result) REQUIRE n.result_id IS UNIQUE",
)

WRITE_PROVENANCE = """
MERGE (c:Case {case_id: $case_id})
MERGE (i:ITD {variant_id: $variant_id})
SET i.gene = $gene, i.type = 'ITD', i.position = $position,
    i.length_bp = $length_bp, i.sequence_sha256 = $sequence_sha256
MERGE (c)-[:HAS_DIAGNOSTIC_ITD]->(i)
MERGE (f:FollowUp {followup_id: $followup_id})
MERGE (c)-[:HAS_FOLLOWUP]->(f)
MERGE (p:Pipeline {pipeline_id: $pipeline_id})
SET p.caller = $caller, p.caller_version = $caller_version,
    p.config_sha256 = $config_sha256
MERGE (f)-[:ANALYZED_BY]->(p)
MERGE (ch:Challenge {challenge_id: $challenge_id})
SET ch.fixture_id = $fixture_id, ch.fixture_sha256 = $fixture_sha256,
    ch.sandbox_id = $sandbox_id, ch.status = $status,
    ch.test_vaf = $test_vaf, ch.completed_at = datetime($completed_at)
MERGE (i)-[:CHALLENGED_IN]->(ch)
MERGE (ch)-[:USED_PIPELINE]->(p)
MERGE (r:Result {result_id: $result_id})
SET r.exact_recovery = $exact_recovery, r.error = $error
MERGE (ch)-[:PRODUCED]->(r)
"""

VERDICT_QUERY = """
MATCH (c:Case {case_id: $case_id})-[:HAS_FOLLOWUP]->(f:FollowUp {followup_id: $followup_id})
MATCH (f)-[:ANALYZED_BY]->(p:Pipeline {pipeline_id: $pipeline_id})
MATCH (c)-[:HAS_DIAGNOSTIC_ITD]->(i:ITD {variant_id: $variant_id})
OPTIONAL MATCH (i)-[:CHALLENGED_IN]->(ch:Challenge {challenge_id: $challenge_id})-[:USED_PIPELINE]->(p)
OPTIONAL MATCH (ch)-[:PRODUCED]->(r:Result)
WITH [o IN collect({status: ch.status, recovered: r.exact_recovery})
      WHERE o.status IS NOT NULL] AS observations
RETURN CASE
  WHEN size(observations) = 0 THEN 'NO_CONCLUSION'
  WHEN any(o IN observations WHERE o.status = 'failed') THEN 'NO_CONCLUSION'
  WHEN any(o IN observations WHERE o.status = 'completed' AND o.recovered = true)
    THEN 'COMPUTATIONALLY_OBSERVABLE'
  WHEN any(o IN observations WHERE o.status = 'completed' AND o.recovered = false)
    THEN 'NOT_TECHNICALLY_COMPARABLE'
  ELSE 'NO_CONCLUSION'
END AS verdict
"""


class Neo4jStore:
    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        truststore.inject_into_ssl()
        self._driver = GraphDatabase.driver(uri, auth=(username, password))
        self._database = database

    def close(self) -> None:
        self._driver.close()

    def verify_connectivity(self) -> None:
        self._driver.verify_connectivity()

    def ensure_constraints(self) -> None:
        for statement in CONSTRAINTS:
            self._driver.execute_query(statement, database_=self._database)

    def write_provenance(self, values: Mapping[str, Any]) -> None:
        self._driver.execute_query(
            WRITE_PROVENANCE,
            parameters_=dict(values),
            database_=self._database,
        )

    def get_verdict(
        self, case_id: str, followup_id: str, pipeline_id: str, variant_id: str,
        challenge_id: str,
    ) -> Verdict:
        records, _, _ = self._driver.execute_query(
            VERDICT_QUERY,
            case_id=case_id,
            followup_id=followup_id,
            pipeline_id=pipeline_id,
            variant_id=variant_id,
            challenge_id=challenge_id,
            database_=self._database,
        )
        if len(records) != 1:
            return Verdict.NO_CONCLUSION
        try:
            return Verdict(records[0]["verdict"])
        except (KeyError, ValueError):
            return Verdict.NO_CONCLUSION
