"""A deterministic finite automaton for the exact phrase WIN PRIZE NOW."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DFATraceStep:
    """One computed transition in a DFA execution."""

    step: int
    current_state: str
    consumed_token: str | None
    next_state: str
    explanation: str
    remaining_input: list[str]


@dataclass(frozen=True)
class DFASimulationResult:
    """The final state and trace produced by running the DFA."""

    input_text: str
    tokens: list[str]
    accepted: bool
    final_state: str
    trace: list[DFATraceStep]


class WinPrizeNowDFA:
    """Recognize exactly three whitespace-separated tokens: WIN PRIZE NOW.

    Tokens are converted to uppercase before processing, so matching is
    case-insensitive. Every unexpected token enters ``q_dead``. The dead state
    loops to itself, which ensures that extra tokens cannot be accepted.
    """

    states = frozenset({"q0", "q1", "q2", "q3", "q_dead"})
    alphabet = frozenset({"WIN", "PRIZE", "NOW", "other"})
    start_state = "q0"
    accepting_states = frozenset({"q3"})
    dead_state = "q_dead"

    # Only these three token/state pairs advance toward the accepting state.
    transition_function = {
        ("q0", "WIN"): "q1",
        ("q1", "PRIZE"): "q2",
        ("q2", "NOW"): "q3",
    }

    expected_tokens = {
        "q0": "WIN",
        "q1": "PRIZE",
        "q2": "NOW",
    }

    @staticmethod
    def tokenize(input_text: str) -> list[str]:
        """Split on whitespace and normalize tokens for case-insensitive matching."""

        return [token.upper() for token in input_text.split()]

    def next_state(self, current_state: str, token: str) -> str:
        """Apply the deterministic transition function to one normalized token."""

        if current_state == self.dead_state:
            return self.dead_state
        return self.transition_function.get((current_state, token), self.dead_state)

    def _explain_transition(
        self, current_state: str, token: str, next_state: str
    ) -> str:
        if current_state == self.dead_state:
            return f"q_dead loops to itself after token {token!r}."
        if next_state == self.dead_state:
            expected = self.expected_tokens.get(current_state)
            if expected is None:
                return (
                    f"State {current_state} was already accepting; extra token "
                    f"{token!r} moves to q_dead."
                )
            return (
                f"State {current_state} expected {expected!r}, but consumed "
                f"{token!r}; move to q_dead."
            )
        return f"Consume {token!r}: {current_state} transitions to {next_state}."

    def simulate(self, input_text: str) -> DFASimulationResult:
        """Execute the DFA rather than comparing against precomputed samples."""

        tokens = self.tokenize(input_text)
        current_state = self.start_state
        trace = [
            DFATraceStep(
                step=0,
                current_state=current_state,
                consumed_token=None,
                next_state=current_state,
                explanation="Begin in start state q0 without consuming input.",
                remaining_input=tokens.copy(),
            )
        ]

        for index, token in enumerate(tokens):
            next_state = self.next_state(current_state, token)
            trace.append(
                DFATraceStep(
                    step=index + 1,
                    current_state=current_state,
                    consumed_token=token,
                    next_state=next_state,
                    explanation=self._explain_transition(
                        current_state, token, next_state
                    ),
                    remaining_input=tokens[index + 1 :],
                )
            )
            current_state = next_state

        # q3 is the only accepting state, so incomplete and empty inputs reject.
        accepted = current_state in self.accepting_states
        return DFASimulationResult(
            input_text=input_text,
            tokens=tokens,
            accepted=accepted,
            final_state=current_state,
            trace=trace,
        )


win_prize_now_dfa = WinPrizeNowDFA()
