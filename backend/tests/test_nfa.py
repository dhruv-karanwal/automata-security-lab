"""Unit tests for the genuine epsilon-NFA."""

import pytest

from app.engines.nfa import phishing_phrases_nfa


@pytest.mark.parametrize(
    ("input_text", "accepting_state"),
    [
        ("WIN PRIZE NOW", "w3"),
        ("CLAIM REWARD NOW", "c3"),
        ("ACCOUNT VERIFY IMMEDIATELY", "a3"),
        ("claim ReWaRd now", "c3"),
    ],
)
def test_nfa_accepts_each_configured_sequence_case_insensitively(
    input_text: str, accepting_state: str
) -> None:
    result = phishing_phrases_nfa.simulate(input_text)

    assert result.accepted is True
    assert result.accepting_states_reached == frozenset({accepting_state})


@pytest.mark.parametrize(
    "input_text",
    [
        "PRIZE WIN NOW",
        "WIN PRIZE",
        "CLAIM REWARD NOW TODAY",
        "ACCOUNT IMMEDIATELY VERIFY",
        "",
    ],
)
def test_nfa_rejects_wrong_partial_extra_and_empty_inputs(input_text: str) -> None:
    result = phishing_phrases_nfa.simulate(input_text)

    assert result.accepted is False
    assert result.accepting_states_reached == frozenset()


def test_epsilon_closure_activates_all_branch_heads() -> None:
    closure = phishing_phrases_nfa.epsilon_closure({"s0"})

    assert closure == frozenset({"s0", "w0", "c0", "a0"})


def test_nfa_tracks_multiple_active_branches_before_first_token() -> None:
    result = phishing_phrases_nfa.simulate("WIN PRIZE NOW")

    assert result.trace[0].active_states_after == frozenset(
        {"s0", "w0", "c0", "a0"}
    )
    assert result.trace[1].active_states_before == frozenset(
        {"s0", "w0", "c0", "a0"}
    )
    assert result.trace[1].active_states_after == frozenset({"w1"})


def test_nfa_trace_records_state_sets_transitions_and_remaining_input() -> None:
    result = phishing_phrases_nfa.simulate("CLAIM REWARD NOW")

    assert result.trace[1].consumed_token == "CLAIM"
    assert result.trace[1].transitions_taken == ("c0 --CLAIM--> c1",)
    assert result.trace[1].active_states_after == frozenset({"c1"})
    assert result.trace[1].remaining_input == ["REWARD", "NOW"]
    assert result.trace[-1].active_states_after == frozenset({"c3"})
    assert result.trace[-1].remaining_input == []
