"""Unit tests for the fixed regular-expression catalogue."""

from app.engines.regex_engine import configured_regex_engine


def matches_for(rule_id: str, subject: str = "", body: str = ""):
    result = configured_regex_engine.scan(subject, body)
    return [match for match in result.matches if match.rule_id == rule_id]


def test_url_rule_matches_valid_http_url() -> None:
    body = "Review https://example.com/verify-account today"
    matches = matches_for("RULE-URL", body=body)

    assert len(matches) == 1
    assert matches[0].matched_text == "https://example.com/verify-account"


def test_email_address_rule_matches_simplified_address() -> None:
    body = "Contact support@service-auth.com for assistance."
    matches = matches_for("RULE-EMAIL", body=body)

    assert len(matches) == 1
    assert matches[0].matched_text == "support@service-auth.com"


def test_urgency_phrases_are_case_insensitive() -> None:
    result = configured_regex_engine.scan(
        "Please win prize now", "You should ClAiM ReWaRd NoW"
    )
    rule_ids = {match.rule_id for match in result.matches}

    assert "RULE-PHRASE-WIN" in rule_ids
    assert "RULE-PHRASE-CLAIM" in rule_ids


def test_repeated_exclamation_marks_are_detected() -> None:
    matches = matches_for("RULE-EXCLAMATION", body="Act now!!! Please!!")

    assert [match.matched_text for match in matches] == ["!!!", "!!"]


def test_ordinary_text_returns_no_matches() -> None:
    result = configured_regex_engine.scan(
        "Weekly planning meeting", "Please review the agenda before tomorrow."
    )

    assert result.matched is False
    assert result.matches == []


def test_match_positions_are_relative_to_subject_and_body() -> None:
    subject = "Alert: WIN PRIZE NOW"
    body = "Contact support@example.com today"
    result = configured_regex_engine.scan(subject, body)
    win_match = next(
        match for match in result.matches if match.rule_id == "RULE-PHRASE-WIN"
    )
    email_match = next(
        match for match in result.matches if match.rule_id == "RULE-EMAIL"
    )

    assert win_match.source == "subject"
    assert (win_match.start_index, win_match.end_index) == (
        subject.index("WIN"),
        subject.index("WIN") + len("WIN PRIZE NOW"),
    )
    assert email_match.source == "body"
    assert body[email_match.start_index : email_match.end_index] == email_match.matched_text


def test_engine_exposes_only_preconfigured_rules() -> None:
    rule_ids = {rule.rule_id for rule in configured_regex_engine.rules}

    assert rule_ids == {
        "RULE-URL",
        "RULE-EMAIL",
        "RULE-PHRASE-WIN",
        "RULE-PHRASE-CLAIM",
        "RULE-PHRASE-VERIFY",
        "RULE-EXCLAMATION",
    }
