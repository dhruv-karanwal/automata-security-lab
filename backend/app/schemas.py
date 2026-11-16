"""Pydantic models for the public Automata Security Lab API.

These models define the wire contract only. They do not execute automata or
regular-expression detection.
"""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


MAX_EMAIL_LENGTH = 10_000
NO_MATCH_WARNING = (
    "No configured patterns matched. This does not guarantee that the message is safe."
)


class AnalysisMode(str, Enum):
    COMBINED = "combined"
    DFA = "dfa"
    NFA = "nfa"
    REGEX = "regex"


class Classification(str, Enum):
    SUSPICIOUS = "suspicious"
    NO_CONFIGURED_PATTERNS_MATCHED = "no_configured_patterns_matched"


class AutomatonType(str, Enum):
    DFA = "dfa"
    NFA = "nfa"


class HealthResponse(BaseModel):
    status: Literal["ok"]
    project: str


class ErrorResponse(BaseModel):
    detail: str


class AnalyzeEmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str = ""
    body: str
    mode: AnalysisMode = AnalysisMode.COMBINED

    @model_validator(mode="after")
    def validate_total_length(self) -> "AnalyzeEmailRequest":
        if len(self.subject) + len(self.body) > MAX_EMAIL_LENGTH:
            raise ValueError(
                f"subject and body together must not exceed {MAX_EMAIL_LENGTH} characters"
            )
        return self


class MatchEvidence(BaseModel):
    source: Literal["subject", "body"]
    text: str
    start_index: int = Field(ge=0)
    end_index: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_index_order(self) -> "MatchEvidence":
        if self.end_index <= self.start_index:
            raise ValueError("end_index must be greater than start_index")
        return self


class MatchedPattern(BaseModel):
    pattern_id: str
    name: str
    category: str
    explanation: str = ""
    evidence: list[MatchEvidence] = Field(min_length=1)


class TransitionTraceStep(BaseModel):
    step: int = Field(ge=0)
    input_index: int = Field(ge=0)
    symbol: str | None = None
    # An NFA can have no active states after a rejecting transition. If more
    # input remains, the next real trace step therefore starts from an empty set.
    states_before: list[str] = Field(default_factory=list)
    states_after: list[str] = Field(default_factory=list)
    transitions_taken: list[str] = Field(default_factory=list)
    explanation: str
    remaining_input: list[str] = Field(default_factory=list)


class DFAAnalysisResult(BaseModel):
    engine: Literal[AnalysisMode.DFA] = AnalysisMode.DFA
    matched: bool
    accepted: bool
    matched_patterns: list[MatchedPattern] = Field(default_factory=list)
    final_states: list[str] = Field(default_factory=list)
    active_states: list[str] = Field(default_factory=list)
    trace: list[TransitionTraceStep] = Field(default_factory=list)
    explanation: str


class NFAAnalysisResult(BaseModel):
    engine: Literal[AnalysisMode.NFA] = AnalysisMode.NFA
    matched: bool
    accepted: bool
    matched_patterns: list[MatchedPattern] = Field(default_factory=list)
    final_states: list[str] = Field(default_factory=list)
    active_states: list[str] = Field(default_factory=list)
    trace: list[TransitionTraceStep] = Field(default_factory=list)
    explanation: str


class RegexAnalysisResult(BaseModel):
    engine: Literal[AnalysisMode.REGEX] = AnalysisMode.REGEX
    matched: bool
    matched_patterns: list[MatchedPattern] = Field(default_factory=list)
    explanation: str


class AnalyzeEmailResponse(BaseModel):
    classification: Classification
    risk_score: int = Field(ge=0, le=100)
    mode: AnalysisMode
    dfa_result: DFAAnalysisResult | None = None
    nfa_result: NFAAnalysisResult | None = None
    regex_result: RegexAnalysisResult | None = None
    no_match_warning: Literal[
        "No configured patterns matched. This does not guarantee that the message is safe."
    ] = NO_MATCH_WARNING

    @model_validator(mode="after")
    def validate_results_for_mode(self) -> "AnalyzeEmailResponse":
        results = {
            AnalysisMode.DFA: self.dfa_result,
            AnalysisMode.NFA: self.nfa_result,
            AnalysisMode.REGEX: self.regex_result,
        }
        if self.mode == AnalysisMode.COMBINED:
            if any(result is None for result in results.values()):
                raise ValueError("combined mode requires DFA, NFA, and regex results")
        else:
            if results[self.mode] is None:
                raise ValueError(f"{self.mode.value} mode requires its matching result")
            if any(
                result is not None
                for engine, result in results.items()
                if engine != self.mode
            ):
                raise ValueError("single-engine mode must not include other engine results")
        return self


class AutomatonTransition(BaseModel):
    from_state: str
    symbol: str | None
    to_states: list[str] = Field(min_length=1)


class AutomatonDescription(BaseModel):
    automaton_id: str
    name: str
    description: str
    automaton_type: AutomatonType
    states: list[str] = Field(min_length=1)
    alphabet: list[str] = Field(default_factory=list)
    start_state: str
    accepting_states: list[str] = Field(default_factory=list)
    transitions: list[AutomatonTransition] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_automaton_references(self) -> "AutomatonDescription":
        state_set = set(self.states)
        alphabet_set = set(self.alphabet)
        if len(state_set) != len(self.states):
            raise ValueError("states must be unique")
        if len(alphabet_set) != len(self.alphabet):
            raise ValueError("alphabet symbols must be unique")
        if self.start_state not in state_set:
            raise ValueError("start_state must be included in states")
        if not set(self.accepting_states).issubset(state_set):
            raise ValueError("accepting_states must be included in states")

        for transition in self.transitions:
            if transition.from_state not in state_set:
                raise ValueError("transition from_state must be included in states")
            if not set(transition.to_states).issubset(state_set):
                raise ValueError("transition to_states must be included in states")
            if transition.symbol is not None and transition.symbol not in alphabet_set:
                raise ValueError("transition symbol must be included in alphabet")
            if self.automaton_type == AutomatonType.DFA:
                if transition.symbol is None:
                    raise ValueError("DFA transitions cannot use epsilon moves")
                if len(transition.to_states) != 1:
                    raise ValueError("each DFA transition must have one destination state")
        return self


class AutomataListResponse(BaseModel):
    automata: list[AutomatonDescription]


class AutomatonSimulationRequest(BaseModel):
    input_text: str = Field(max_length=MAX_EMAIL_LENGTH)


class AutomatonSimulationResponse(BaseModel):
    automaton_id: str
    automaton_type: AutomatonType
    input_text: str
    accepted: bool
    final_states: list[str] = Field(default_factory=list)
    active_states: list[str] = Field(default_factory=list)
    trace: list[TransitionTraceStep] = Field(default_factory=list)
    explanation: str


class SubsetStateDescription(BaseModel):
    state_id: str
    nfa_states: list[str] = Field(default_factory=list)
    is_start: bool
    is_accepting: bool


class SubsetDFATransition(BaseModel):
    from_state: str
    symbol: str
    to_state: str


class SubsetConstructionStepDescription(BaseModel):
    step: int = Field(ge=1)
    source_state: str
    source_nfa_states: list[str] = Field(default_factory=list)
    symbol: str
    move_result: list[str] = Field(default_factory=list)
    epsilon_closure: list[str] = Field(default_factory=list)
    target_state: str
    created_new_state: bool


class NFAConversionResponse(BaseModel):
    source_automaton_id: str
    source_start_state: str
    source_accepting_states: list[str]
    alphabet: list[str]
    initial_epsilon_closure: list[str]
    dfa_start_state: str
    dfa_accepting_states: list[str]
    dfa_states: list[SubsetStateDescription]
    transitions: list[SubsetDFATransition]
    construction_steps: list[SubsetConstructionStepDescription]
    explanation: str


class PDFExtractionResponse(BaseModel):
    filename: str
    extracted_text: str
    page_count: int = Field(ge=1)
    character_count: int = Field(ge=1)
    extraction_note: str
