"""Mathematical tests for epsilon-NFA to DFA subset construction."""

from copy import deepcopy
from itertools import product

from app.engines.nfa import phishing_phrases_nfa
from app.engines.subset_construction import (
    convert_nfa_to_dfa,
    epsilon_closure,
)


def test_epsilon_closure_follows_nested_epsilon_transitions() -> None:
    relation = {
        ("p0", None): frozenset({"p1", "p2"}),
        ("p1", None): frozenset({"p3"}),
    }

    assert epsilon_closure({"p0"}, relation) == frozenset(
        {"p0", "p1", "p2", "p3"}
    )


def test_subset_construction_handles_multiple_destinations_for_one_symbol() -> None:
    """This teaching NFA has genuine same-state/same-symbol branching."""

    result = convert_nfa_to_dfa(
        states={"p0", "p1", "p2"},
        alphabet={"A"},
        start_state="p0",
        accepting_states={"p2"},
        transition_relation={
            ("p0", "A"): frozenset({"p1", "p2"}),
            ("p1", "A"): frozenset({"p2"}),
        },
    )

    branched_state = next(
        state for state in result.states if state.nfa_states == {"p1", "p2"}
    )
    assert branched_state.is_accepting is True
    assert len(result.states) > 1
    assert result.accepts(["A"]) is True


def test_empty_subset_is_a_total_dead_state() -> None:
    result = convert_nfa_to_dfa(
        states={"p0", "p1"},
        alphabet={"A", "B"},
        start_state="p0",
        accepting_states={"p1"},
        transition_relation={("p0", "A"): frozenset({"p1"})},
    )

    dead = next(state for state in result.states if state.state_id == "D_dead")
    assert dead.nfa_states == frozenset()
    assert dead.is_accepting is False
    dead_transitions = {
        transition.symbol: transition.to_state
        for transition in result.transitions
        if transition.from_state == "D_dead"
    }
    assert dead_transitions == {"A": "D_dead", "B": "D_dead"}


def test_accepting_state_propagates_to_every_subset_that_contains_it() -> None:
    result = convert_nfa_to_dfa(
        states={"p0", "p1", "p2"},
        alphabet={"A"},
        start_state="p0",
        accepting_states={"p2"},
        transition_relation={
            ("p0", None): frozenset({"p1"}),
            ("p0", "A"): frozenset({"p2"}),
            ("p1", "A"): frozenset({"p1"}),
        },
    )

    accepting_subsets = [state for state in result.states if state.is_accepting]
    assert accepting_subsets
    assert all("p2" in state.nfa_states for state in accepting_subsets)
    assert {state.state_id for state in accepting_subsets} == result.accepting_states


def test_conversion_does_not_mutate_the_original_nfa() -> None:
    original_relation = deepcopy(phishing_phrases_nfa.transition_relation)
    original_states = phishing_phrases_nfa.states

    _convert_email_nfa()

    assert phishing_phrases_nfa.transition_relation == original_relation
    assert phishing_phrases_nfa.states == original_states


def test_generated_dfa_is_language_equivalent_for_exhaustive_short_inputs() -> None:
    """Compare executions, rather than comparing two prewritten tables."""

    converted = _convert_email_nfa()
    alphabet = sorted(phishing_phrases_nfa.alphabet)

    for length in range(4):
        for symbols in product(alphabet, repeat=length):
            nfa_accepted = phishing_phrases_nfa.simulate(" ".join(symbols)).accepted
            assert converted.accepts(symbols) is nfa_accepted

    edge_cases = [
        ("WIN", "PRIZE", "NOW", "NOW"),
        ("CLAIM", "REWARD", "NOW", "WIN"),
        ("ACCOUNT", "VERIFY", "IMMEDIATELY", "PRIZE"),
    ]
    for symbols in edge_cases:
        assert converted.accepts(symbols) is False
        assert phishing_phrases_nfa.simulate(" ".join(symbols)).accepted is False


def _convert_email_nfa():
    return convert_nfa_to_dfa(
        states=set(phishing_phrases_nfa.states),
        alphabet=set(phishing_phrases_nfa.alphabet),
        start_state=phishing_phrases_nfa.start_state,
        accepting_states=set(phishing_phrases_nfa.accepting_states),
        transition_relation=phishing_phrases_nfa.transition_relation,
    )
