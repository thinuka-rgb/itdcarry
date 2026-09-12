from backend.neo4j_store import CONSTRAINTS, VERDICT_QUERY, WRITE_PROVENANCE


def test_constraints_cover_stable_nodes():
    rendered = "\n".join(CONSTRAINTS)
    for field in (
        "case_id",
        "variant_id",
        "followup_id",
        "pipeline_id",
        "challenge_id",
        "result_id",
    ):
        assert field in rendered


def test_provenance_links_followup_pipeline_and_challenge():
    assert "(f)-[:ANALYZED_BY]->(p)" in WRITE_PROVENANCE
    assert "(ch)-[:USED_PIPELINE]->(p)" in WRITE_PROVENANCE


def test_verdict_fails_closed():
    assert "size(observations) = 0 THEN 'NO_CONCLUSION'" in VERDICT_QUERY
    assert "o.status = 'failed'" in VERDICT_QUERY

