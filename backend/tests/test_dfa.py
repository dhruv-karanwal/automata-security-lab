"""Unit tests for the genuine WIN PRIZE NOW DFA."""

import pytest

from app.engines.dfa import win_prize_now_dfa


@pytest.mark.parametrize(
    "input_text",
    ["WIN PRIZE NOW", "win prize now", "WiN pRiZe NoW", "  WIN   PRIZE\tNOW  "],
)
def test_dfa_accepts_exact_sequence_case_insensitively(input_text: str) -> None:
    result = win_prize_now_dfa.simulate(input_text)

    assert result.accepted is True
    assert result.final_state == "q3"


@pytest.mark.parametrize(
    ("input_text", "expected_final_state"),
    [
        ("WIN NOW PRIZE", "q_dead"),
        ("WIN PRIZE", "q2"),
        ("WIN PRIZE NOW TODAY", "q_dead"),
        ("", "q0"),
    ],
)
def test_dfa_rejects_non_exact_sequences(
    input_text: str, expected_final_state: str
) -> None:
    result = win_prize_now_dfa.simulate(input_text)

    assert result.accepted is False
    assert result.final_state == expected_final_state


def test_dfa_trace_records_computed_transitions() -> None:
    result = win_prize_now_dfa.simulate("WIN PRIZE NOW")

    assert [
        (step.current_state, step.consumed_token, step.next_state)
        for step in result.trace
    ] == [
        ("q0", None, "q0"),
        ("q0", "WIN", "q1"),
        ("q1", "PRIZE", "q2"),
        ("q2", "NOW", "q3"),
    ]
    assert result.trace[1].remaining_input == ["PRIZE", "NOW"]
    assert result.trace[-1].remaining_input == []
