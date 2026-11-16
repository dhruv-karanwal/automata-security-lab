"""Reusable epsilon-NFA to DFA subset construction.

The converter works from formal components rather than a precomputed table. It
does not mutate the source NFA. Reachable subsets are discovered breadth-first
until every generated state has a transition for every alphabet symbol.
"""

from collections import deque
from dataclasses import dataclass
from typing import Mapping


EPSILON = None
TransitionRelation = Mapping[tuple[str, str | None], frozenset[str]]


@dataclass(frozen=True)
class GeneratedSubsetState:
    state_id: str
    nfa_states: frozenset[str]
    is_start: bool
    is_accepting: bool


@dataclass(frozen=True)
class GeneratedDFATransition:
    from_state: str
    symbol: str
    to_state: str


@dataclass(frozen=True)
class SubsetConstructionStep:
    step: int
    source_state: str
    source_nfa_states: frozenset[str]
    symbol: str
    move_result: frozenset[str]
    epsilon_closure: frozenset[str]
    target_state: str
    created_new_state: bool


@dataclass(frozen=True)
class SubsetConstructionResult:
    alphabet: tuple[str, ...]
    initial_epsilon_closure: frozenset[str]
    start_state: str
    states: tuple[GeneratedSubsetState, ...]
    accepting_states: frozenset[str]
    transitions: tuple[GeneratedDFATransition, ...]
    steps: tuple[SubsetConstructionStep, ...]

    def accepts(self, symbols: list[str] | tuple[str, ...]) -> bool:
        """Execute the generated deterministic transition table."""

        transition_map = {
            (transition.from_state, transition.symbol): transition.to_state
            for transition in self.transitions
        }
        state = self.start_state
        for symbol in symbols:
            state = transition_map[(state, symbol)]
        return state in self.accepting_states


def epsilon_closure(
    seed_states: set[str] | frozenset[str],
    transition_relation: TransitionRelation,
) -> frozenset[str]:
    """Return all states reachable with zero or more epsilon transitions."""

    closure = set(seed_states)
    pending = list(seed_states)
    while pending:
        state = pending.pop()
        for next_state in transition_relation.get((state, EPSILON), frozenset()):
            if next_state not in closure:
                closure.add(next_state)
                pending.append(next_state)
    return frozenset(closure)


def move(
    states: set[str] | frozenset[str],
    symbol: str,
    transition_relation: TransitionRelation,
) -> frozenset[str]:
    """Union every NFA destination for one symbol from an active-state set."""

    destinations: set[str] = set()
    for state in states:
        destinations.update(
            transition_relation.get((state, symbol), frozenset())
        )
    return frozenset(destinations)


def convert_nfa_to_dfa(
    *,
    states: set[str] | frozenset[str],
    alphabet: set[str] | frozenset[str],
    start_state: str,
    accepting_states: set[str] | frozenset[str],
    transition_relation: TransitionRelation,
    max_states: int = 256,
) -> SubsetConstructionResult:
    """Construct the reachable equivalent DFA using the subset algorithm."""

    state_set = frozenset(states)
    alphabet_order = tuple(sorted(alphabet))
    accepting_set = frozenset(accepting_states)
    if start_state not in state_set:
        raise ValueError("start_state must belong to states")
    if not accepting_set.issubset(state_set):
        raise ValueError("accepting_states must belong to states")

    initial_subset = epsilon_closure({start_state}, transition_relation)
    subset_to_id: dict[frozenset[str], str] = {initial_subset: "D0"}
    subset_queue: deque[frozenset[str]] = deque([initial_subset])
    generated_states: list[GeneratedSubsetState] = [
        GeneratedSubsetState(
            state_id="D0",
            nfa_states=initial_subset,
            is_start=True,
            is_accepting=bool(initial_subset & accepting_set),
        )
    ]
    generated_transitions: list[GeneratedDFATransition] = []
    construction_steps: list[SubsetConstructionStep] = []
    numbered_state_count = 1

    while subset_queue:
        source_subset = subset_queue.popleft()
        source_id = subset_to_id[source_subset]
        for symbol in alphabet_order:
            moved = move(source_subset, symbol, transition_relation)
            target_subset = epsilon_closure(moved, transition_relation)
            created_new_state = target_subset not in subset_to_id

            if created_new_state:
                if len(subset_to_id) >= max_states:
                    raise ValueError(f"Subset construction exceeds the {max_states}-state educational limit.")
                if not target_subset:
                    target_id = "D_dead"
                else:
                    target_id = f"D{numbered_state_count}"
                    numbered_state_count += 1
                subset_to_id[target_subset] = target_id
                subset_queue.append(target_subset)
                generated_states.append(
                    GeneratedSubsetState(
                        state_id=target_id,
                        nfa_states=target_subset,
                        is_start=False,
                        is_accepting=bool(target_subset & accepting_set),
                    )
                )
            else:
                target_id = subset_to_id[target_subset]

            generated_transitions.append(
                GeneratedDFATransition(
                    from_state=source_id,
                    symbol=symbol,
                    to_state=target_id,
                )
            )
            construction_steps.append(
                SubsetConstructionStep(
                    step=len(construction_steps) + 1,
                    source_state=source_id,
                    source_nfa_states=source_subset,
                    symbol=symbol,
                    move_result=moved,
                    epsilon_closure=target_subset,
                    target_state=target_id,
                    created_new_state=created_new_state,
                )
            )

    return SubsetConstructionResult(
        alphabet=alphabet_order,
        initial_epsilon_closure=initial_subset,
        start_state="D0",
        states=tuple(generated_states),
        accepting_states=frozenset(
            state.state_id for state in generated_states if state.is_accepting
        ),
        transitions=tuple(generated_transitions),
        steps=tuple(construction_steps),
    )
