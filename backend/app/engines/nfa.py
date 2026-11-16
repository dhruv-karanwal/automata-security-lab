"""NFA with epsilon branches for three configured suspicious phrases."""

from dataclasses import dataclass


EPSILON = None


@dataclass(frozen=True)
class NFATraceStep:
    """One active-state-set update during an NFA execution."""

    step: int
    consumed_token: str | None
    active_states_before: frozenset[str]
    transitions_taken: tuple[str, ...]
    active_states_after: frozenset[str]
    remaining_input: list[str]


@dataclass(frozen=True)
class NFASimulationResult:
    input_text: str
    tokens: list[str]
    accepted: bool
    active_states: frozenset[str]
    accepting_states_reached: frozenset[str]
    trace: list[NFATraceStep]


class PhishingPhrasesNFA:
    """Recognize three exact token sequences using nondeterministic branches.

    An epsilon transition changes state without consuming an input token. The
    epsilon closure of a set contains every state reachable using zero or more
    epsilon transitions. Starting at ``s0`` therefore activates all three
    branch heads before the first token is read.
    """

    states = frozenset(
        {
            "s0",
            "w0", "w1", "w2", "w3",
            "c0", "c1", "c2", "c3",
            "a0", "a1", "a2", "a3",
        }
    )
    alphabet = frozenset(
        {
            "WIN", "PRIZE", "NOW", "CLAIM", "REWARD", "ACCOUNT", "VERIFY",
            "IMMEDIATELY",
        }
    )
    start_state = "s0"
    accepting_states = frozenset({"w3", "c3", "a3"})

    # A transition relation maps one (state, symbol) pair to a SET of states.
    # None represents epsilon: no input token is consumed for that move.
    transition_relation = {
        ("s0", EPSILON): frozenset({"w0", "c0", "a0"}),
        ("w0", "WIN"): frozenset({"w1"}),
        ("w1", "PRIZE"): frozenset({"w2"}),
        ("w2", "NOW"): frozenset({"w3"}),
        ("c0", "CLAIM"): frozenset({"c1"}),
        ("c1", "REWARD"): frozenset({"c2"}),
        ("c2", "NOW"): frozenset({"c3"}),
        ("a0", "ACCOUNT"): frozenset({"a1"}),
        ("a1", "VERIFY"): frozenset({"a2"}),
        ("a2", "IMMEDIATELY"): frozenset({"a3"}),
    }

    @staticmethod
    def tokenize(input_text: str) -> list[str]:
        """Split on whitespace and uppercase tokens for case-insensitive matching."""

        return [token.upper() for token in input_text.split()]

    def epsilon_closure(self, states: set[str] | frozenset[str]) -> frozenset[str]:
        """Follow every reachable epsilon move until no new states remain."""

        closure = set(states)
        states_to_visit = list(states)
        while states_to_visit:
            state = states_to_visit.pop()
            for next_state in self.transition_relation.get(
                (state, EPSILON), frozenset()
            ):
                if next_state not in closure:
                    closure.add(next_state)
                    states_to_visit.append(next_state)
        return frozenset(closure)

    def move(
        self, active_states: frozenset[str], token: str
    ) -> tuple[frozenset[str], tuple[str, ...]]:
        """Take every matching transition from the current active state set."""

        destination_states: set[str] = set()
        transitions_taken: list[str] = []
        for state in sorted(active_states):
            for next_state in sorted(
                self.transition_relation.get((state, token), frozenset())
            ):
                destination_states.add(next_state)
                transitions_taken.append(f"{state} --{token}--> {next_state}")

        # Epsilon moves may activate more states after a token transition.
        return self.epsilon_closure(destination_states), tuple(transitions_taken)

    def simulate(self, input_text: str) -> NFASimulationResult:
        tokens = self.tokenize(input_text)
        active_states = self.epsilon_closure({self.start_state})
        trace = [
            NFATraceStep(
                step=0,
                consumed_token=None,
                active_states_before=frozenset({self.start_state}),
                transitions_taken=(
                    "s0 --ε--> a0",
                    "s0 --ε--> c0",
                    "s0 --ε--> w0",
                ),
                active_states_after=active_states,
                remaining_input=tokens.copy(),
            )
        ]

        for index, token in enumerate(tokens):
            states_before = active_states
            active_states, transitions_taken = self.move(states_before, token)
            trace.append(
                NFATraceStep(
                    step=index + 1,
                    consumed_token=token,
                    active_states_before=states_before,
                    transitions_taken=transitions_taken,
                    active_states_after=active_states,
                    remaining_input=tokens[index + 1 :],
                )
            )

        accepting_states_reached = active_states & self.accepting_states
        return NFASimulationResult(
            input_text=input_text,
            tokens=tokens,
            accepted=bool(accepting_states_reached),
            active_states=active_states,
            accepting_states_reached=accepting_states_reached,
            trace=trace,
        )


phishing_phrases_nfa = PhishingPhrasesNFA()
