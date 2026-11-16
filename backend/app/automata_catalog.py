"""Static automaton descriptions; this module performs no simulation."""

from app.schemas import AutomatonDescription


AUTOMATA = (
    AutomatonDescription(
        automaton_id="dfa_win_prize_now",
        name="DFA: WIN PRIZE NOW",
        description="Recognizes exactly the token sequence WIN PRIZE NOW.",
        automaton_type="dfa",
        states=["q0", "q1", "q2", "q3", "q_dead"],
        alphabet=["WIN", "PRIZE", "NOW", "other"],
        start_state="q0",
        accepting_states=["q3"],
        transitions=[
            {"from_state": "q0", "symbol": "WIN", "to_states": ["q1"]},
            {"from_state": "q0", "symbol": "PRIZE", "to_states": ["q_dead"]},
            {"from_state": "q0", "symbol": "NOW", "to_states": ["q_dead"]},
            {"from_state": "q0", "symbol": "other", "to_states": ["q_dead"]},
            {"from_state": "q1", "symbol": "WIN", "to_states": ["q_dead"]},
            {"from_state": "q1", "symbol": "PRIZE", "to_states": ["q2"]},
            {"from_state": "q1", "symbol": "NOW", "to_states": ["q_dead"]},
            {"from_state": "q1", "symbol": "other", "to_states": ["q_dead"]},
            {"from_state": "q2", "symbol": "WIN", "to_states": ["q_dead"]},
            {"from_state": "q2", "symbol": "PRIZE", "to_states": ["q_dead"]},
            {"from_state": "q2", "symbol": "NOW", "to_states": ["q3"]},
            {"from_state": "q2", "symbol": "other", "to_states": ["q_dead"]},
            {"from_state": "q3", "symbol": "WIN", "to_states": ["q_dead"]},
            {"from_state": "q3", "symbol": "PRIZE", "to_states": ["q_dead"]},
            {"from_state": "q3", "symbol": "NOW", "to_states": ["q_dead"]},
            {"from_state": "q3", "symbol": "other", "to_states": ["q_dead"]},
            {"from_state": "q_dead", "symbol": "WIN", "to_states": ["q_dead"]},
            {"from_state": "q_dead", "symbol": "PRIZE", "to_states": ["q_dead"]},
            {"from_state": "q_dead", "symbol": "NOW", "to_states": ["q_dead"]},
            {"from_state": "q_dead", "symbol": "other", "to_states": ["q_dead"]},
        ],
    ),
    AutomatonDescription(
        automaton_id="nfa_phishing_branches",
        name="NFA: Multi-Branch Phishing Recognizer",
        description="Describes three token-sequence branches reached by epsilon moves.",
        automaton_type="nfa",
        states=[
            "s0", "w0", "w1", "w2", "w3", "c0", "c1", "c2", "c3",
            "a0", "a1", "a2", "a3",
        ],
        alphabet=[
            "WIN", "PRIZE", "NOW", "CLAIM", "REWARD", "ACCOUNT", "VERIFY",
            "IMMEDIATELY",
        ],
        start_state="s0",
        accepting_states=["w3", "c3", "a3"],
        transitions=[
            {"from_state": "s0", "symbol": None, "to_states": ["w0", "c0", "a0"]},
            {"from_state": "w0", "symbol": "WIN", "to_states": ["w1"]},
            {"from_state": "w1", "symbol": "PRIZE", "to_states": ["w2"]},
            {"from_state": "w2", "symbol": "NOW", "to_states": ["w3"]},
            {"from_state": "c0", "symbol": "CLAIM", "to_states": ["c1"]},
            {"from_state": "c1", "symbol": "REWARD", "to_states": ["c2"]},
            {"from_state": "c2", "symbol": "NOW", "to_states": ["c3"]},
            {"from_state": "a0", "symbol": "ACCOUNT", "to_states": ["a1"]},
            {"from_state": "a1", "symbol": "VERIFY", "to_states": ["a2"]},
            {"from_state": "a2", "symbol": "IMMEDIATELY", "to_states": ["a3"]},
        ],
    ),
)

AUTOMATA_BY_ID = {automaton.automaton_id: automaton for automaton in AUTOMATA}
