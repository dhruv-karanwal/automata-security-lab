"""FastAPI entry point for the Automata Security Lab backend."""

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.automata_catalog import AUTOMATA, AUTOMATA_BY_ID
from app.lab import router as lab_router
from app.engines.dfa import DFASimulationResult, win_prize_now_dfa
from app.engines.nfa import NFASimulationResult, phishing_phrases_nfa
from app.engines.regex_engine import configured_regex_engine
from app.engines.subset_construction import convert_nfa_to_dfa
from app.pdf_extraction import MAX_PDF_SIZE, PDFExtractionError, extract_pdf_text
from app.schemas import (
    AnalysisMode,
    AnalyzeEmailRequest,
    AnalyzeEmailResponse,
    AutomataListResponse,
    AutomatonDescription,
    AutomatonSimulationRequest,
    AutomatonSimulationResponse,
    Classification,
    DFAAnalysisResult,
    ErrorResponse,
    HealthResponse,
    MatchEvidence,
    MatchedPattern,
    NFAAnalysisResult,
    NFAConversionResponse,
    PDFExtractionResponse,
    RegexAnalysisResult,
    SubsetConstructionStepDescription,
    SubsetDFATransition,
    SubsetStateDescription,
    TransitionTraceStep,
)


FRONTEND_ORIGIN = "http://localhost:3000"
DFA_AUTOMATON_ID = "dfa_win_prize_now"
NFA_AUTOMATON_ID = "nfa_phishing_branches"

app = FastAPI(title="Automata Security Lab")
app.include_router(lab_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


@app.get("/api/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", project="Automata Security Lab")


@app.post("/api/pdf/extract", response_model=PDFExtractionResponse)
async def extract_uploaded_pdf(file: UploadFile = File(...)) -> PDFExtractionResponse:
    """Extract selectable PDF text in memory; uploaded bytes are not retained."""

    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only .pdf files are accepted.")
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=415, detail="The uploaded file must be a PDF.")

    data = await file.read(MAX_PDF_SIZE + 1)
    await file.close()
    if len(data) > MAX_PDF_SIZE:
        raise HTTPException(status_code=413, detail="PDF files must be 10 MB or smaller.")
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded PDF is empty.")

    try:
        extracted = extract_pdf_text(data)
    except PDFExtractionError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return PDFExtractionResponse(
        filename=filename,
        extracted_text=extracted.text,
        page_count=extracted.page_count,
        character_count=len(extracted.text),
        extraction_note=(
            "Selectable text was extracted locally in memory. Review and edit it "
            "before analysis if the PDF layout changed the reading order."
        ),
    )


@app.get("/api/automata", response_model=AutomataListResponse)
def list_automata() -> AutomataListResponse:
    return AutomataListResponse(automata=list(AUTOMATA))


@app.get(
    "/api/automata/{automaton_id}",
    response_model=AutomatonDescription,
    responses={404: {"model": ErrorResponse}},
)
def get_automaton(automaton_id: str) -> AutomatonDescription:
    automaton = AUTOMATA_BY_ID.get(automaton_id)
    if automaton is None:
        raise HTTPException(status_code=404, detail="Automaton not found.")
    return automaton


@app.get(
    "/api/automata/{automaton_id}/convert-to-dfa",
    response_model=NFAConversionResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def convert_automaton_to_dfa(automaton_id: str) -> NFAConversionResponse:
    automaton = AUTOMATA_BY_ID.get(automaton_id)
    if automaton is None:
        raise HTTPException(status_code=404, detail="Automaton not found.")
    if automaton_id != NFA_AUTOMATON_ID:
        raise HTTPException(
            status_code=400,
            detail="Subset construction requires the configured NFA.",
        )

    conversion = convert_nfa_to_dfa(
        states=set(phishing_phrases_nfa.states),
        alphabet=set(phishing_phrases_nfa.alphabet),
        start_state=phishing_phrases_nfa.start_state,
        accepting_states=set(phishing_phrases_nfa.accepting_states),
        transition_relation=phishing_phrases_nfa.transition_relation,
    )
    return NFAConversionResponse(
        source_automaton_id=NFA_AUTOMATON_ID,
        source_start_state=phishing_phrases_nfa.start_state,
        source_accepting_states=sorted(phishing_phrases_nfa.accepting_states),
        alphabet=list(conversion.alphabet),
        initial_epsilon_closure=sorted(conversion.initial_epsilon_closure),
        dfa_start_state=conversion.start_state,
        dfa_accepting_states=sorted(conversion.accepting_states),
        dfa_states=[
            SubsetStateDescription(
                state_id=state.state_id,
                nfa_states=sorted(state.nfa_states),
                is_start=state.is_start,
                is_accepting=state.is_accepting,
            )
            for state in conversion.states
        ],
        transitions=[
            SubsetDFATransition(
                from_state=transition.from_state,
                symbol=transition.symbol,
                to_state=transition.to_state,
            )
            for transition in conversion.transitions
        ],
        construction_steps=[
            SubsetConstructionStepDescription(
                step=step.step,
                source_state=step.source_state,
                source_nfa_states=sorted(step.source_nfa_states),
                symbol=step.symbol,
                move_result=sorted(step.move_result),
                epsilon_closure=sorted(step.epsilon_closure),
                target_state=step.target_state,
                created_new_state=step.created_new_state,
            )
            for step in conversion.steps
        ],
        explanation=(
            "Each generated DFA state represents an epsilon-closed set of NFA "
            "states. A generated state is accepting when its subset contains at "
            "least one accepting NFA state. D_dead represents the empty subset."
        ),
    )


@app.post(
    "/api/analyze",
    response_model=AnalyzeEmailResponse,
)
def analyze_email(_request: AnalyzeEmailRequest) -> AnalyzeEmailResponse:
    if _request.mode == AnalysisMode.REGEX:
        return _analyze_with_regex(_request.subject, _request.body)

    source = "body" if _request.body.strip() else "subject"
    input_text = _request.body if source == "body" else _request.subject
    if _request.mode == AnalysisMode.DFA:
        return _analyze_with_dfa(input_text, source)
    if _request.mode == AnalysisMode.NFA:
        return _analyze_with_nfa(input_text, source)
    return _analyze_combined(
        subject=_request.subject,
        body=_request.body,
        automaton_input=input_text,
        automaton_source=source,
    )


def _analyze_combined(
    subject: str, body: str, automaton_input: str, automaton_source: str
) -> AnalyzeEmailResponse:
    """Run all real engines and combine their independently computed results.

    DFA and NFA keep their existing exact-input behavior: they analyze the body,
    or the subject only when the body is blank. Regex scans both fields and keeps
    source-relative evidence offsets.
    """

    dfa_response = _analyze_with_dfa(automaton_input, automaton_source)
    nfa_response = _analyze_with_nfa(automaton_input, automaton_source)
    regex_response = _analyze_with_regex(subject, body)

    detector_scores = (
        dfa_response.risk_score,
        nfa_response.risk_score,
        regex_response.risk_score,
    )
    any_match = any(score > 0 for score in detector_scores)
    return AnalyzeEmailResponse(
        classification=(
            Classification.SUSPICIOUS
            if any_match
            else Classification.NO_CONFIGURED_PATTERNS_MATCHED
        ),
        # Preserve each single-engine score and use the strongest as the combined
        # educational heuristic. This score is not a phishing probability.
        risk_score=max(detector_scores),
        mode=AnalysisMode.COMBINED,
        dfa_result=dfa_response.dfa_result,
        nfa_result=nfa_response.nfa_result,
        regex_result=regex_response.regex_result,
    )


def _analyze_with_dfa(input_text: str, source: str) -> AnalyzeEmailResponse:
    result = win_prize_now_dfa.simulate(input_text)
    matched_patterns = []
    if result.accepted:
        stripped_text = input_text.strip()
        start_index = len(input_text) - len(input_text.lstrip())
        matched_patterns.append(
            MatchedPattern(
                pattern_id=DFA_AUTOMATON_ID,
                name="Exact sequence: WIN PRIZE NOW",
                category="suspicious_phrase",
                evidence=[
                    MatchEvidence(
                        source=source,
                        text=stripped_text,
                        start_index=start_index,
                        end_index=start_index + len(stripped_text),
                    )
                ],
            )
        )

    return AnalyzeEmailResponse(
        classification=(
            Classification.SUSPICIOUS
            if result.accepted
            else Classification.NO_CONFIGURED_PATTERNS_MATCHED
        ),
        risk_score=100 if result.accepted else 0,
        mode=AnalysisMode.DFA,
        dfa_result=DFAAnalysisResult(
            matched=result.accepted,
            accepted=result.accepted,
            matched_patterns=matched_patterns,
            final_states=[result.final_state],
            active_states=[result.final_state],
            trace=_dfa_to_api_trace(result),
            explanation=_dfa_explanation(result.accepted),
        ),
    )


@app.post(
    "/api/automata/{automaton_id}/simulate",
    response_model=AutomatonSimulationResponse,
    responses={404: {"model": ErrorResponse}, 501: {"model": ErrorResponse}},
)
def simulate_automaton(
    automaton_id: str, _request: AutomatonSimulationRequest
) -> AutomatonSimulationResponse:
    if automaton_id not in AUTOMATA_BY_ID:
        raise HTTPException(status_code=404, detail="Automaton not found.")
    if automaton_id == DFA_AUTOMATON_ID:
        result = win_prize_now_dfa.simulate(_request.input_text)
        return AutomatonSimulationResponse(
            automaton_id=DFA_AUTOMATON_ID,
            automaton_type="dfa",
            input_text=_request.input_text,
            accepted=result.accepted,
            final_states=[result.final_state],
            active_states=[result.final_state],
            trace=_dfa_to_api_trace(result),
            explanation=_dfa_explanation(result.accepted),
        )

    result = phishing_phrases_nfa.simulate(_request.input_text)
    active_states = sorted(result.active_states)
    return AutomatonSimulationResponse(
        automaton_id=NFA_AUTOMATON_ID,
        automaton_type="nfa",
        input_text=_request.input_text,
        accepted=result.accepted,
        final_states=sorted(result.accepting_states_reached),
        active_states=active_states,
        trace=_nfa_to_api_trace(result),
        explanation=_nfa_explanation(result.accepted),
    )


def _dfa_to_api_trace(result: DFASimulationResult) -> list[TransitionTraceStep]:
    return [
        TransitionTraceStep(
            step=item.step,
            input_index=max(item.step - 1, 0),
            symbol=item.consumed_token,
            states_before=[item.current_state],
            states_after=[item.next_state],
            explanation=item.explanation,
            remaining_input=item.remaining_input,
        )
        for item in result.trace
    ]


def _nfa_to_api_trace(result: NFASimulationResult) -> list[TransitionTraceStep]:
    return [
        TransitionTraceStep(
            step=item.step,
            input_index=max(item.step - 1, 0),
            symbol=item.consumed_token,
            states_before=sorted(item.active_states_before),
            states_after=sorted(item.active_states_after),
            transitions_taken=list(item.transitions_taken),
            explanation=(
                "Apply epsilon closure before reading input."
                if item.consumed_token is None
                else (
                    "; ".join(item.transitions_taken)
                    if item.transitions_taken
                    else f"No active state has a transition for {item.consumed_token!r}."
                )
            ),
            remaining_input=item.remaining_input,
        )
        for item in result.trace
    ]


def _dfa_explanation(accepted: bool) -> str:
    if accepted:
        return "The complete input matched the configured sequence WIN PRIZE NOW."
    return (
        "The input did not exactly match WIN PRIZE NOW. This means only that this "
        "configured DFA pattern was not matched; it does not guarantee safety."
    )


def _analyze_with_nfa(input_text: str, source: str) -> AnalyzeEmailResponse:
    result = phishing_phrases_nfa.simulate(input_text)
    pattern_names = {
        "w3": ("nfa_win_prize_now", "Exact sequence: WIN PRIZE NOW"),
        "c3": ("nfa_claim_reward_now", "Exact sequence: CLAIM REWARD NOW"),
        "a3": (
            "nfa_account_verify_immediately",
            "Exact sequence: ACCOUNT VERIFY IMMEDIATELY",
        ),
    }
    matched_patterns = []
    stripped_text = input_text.strip()
    start_index = len(input_text) - len(input_text.lstrip())
    for accepting_state in sorted(result.accepting_states_reached):
        pattern_id, name = pattern_names[accepting_state]
        matched_patterns.append(
            MatchedPattern(
                pattern_id=pattern_id,
                name=name,
                category="suspicious_phrase",
                evidence=[
                    MatchEvidence(
                        source=source,
                        text=stripped_text,
                        start_index=start_index,
                        end_index=start_index + len(stripped_text),
                    )
                ],
            )
        )

    return AnalyzeEmailResponse(
        classification=(
            Classification.SUSPICIOUS
            if result.accepted
            else Classification.NO_CONFIGURED_PATTERNS_MATCHED
        ),
        risk_score=100 if result.accepted else 0,
        mode=AnalysisMode.NFA,
        nfa_result=NFAAnalysisResult(
            matched=result.accepted,
            accepted=result.accepted,
            matched_patterns=matched_patterns,
            final_states=sorted(result.accepting_states_reached),
            active_states=sorted(result.active_states),
            trace=_nfa_to_api_trace(result),
            explanation=_nfa_explanation(result.accepted),
        ),
    )


def _nfa_explanation(accepted: bool) -> str:
    if accepted:
        return (
            "At least one NFA path accepted a configured phrase. This pattern match "
            "is not, by itself, proof that the email is malicious."
        )
    return (
        "No NFA path accepted a configured phrase. This does not guarantee that "
        "the email is safe."
    )


def _analyze_with_regex(subject: str, body: str) -> AnalyzeEmailResponse:
    result = configured_regex_engine.scan(subject, body)
    patterns_by_id: dict[str, MatchedPattern] = {}
    for match in result.matches:
        evidence = MatchEvidence(
            source=match.source,
            text=match.matched_text,
            start_index=match.start_index,
            end_index=match.end_index,
        )
        existing = patterns_by_id.get(match.rule_id)
        if existing is None:
            patterns_by_id[match.rule_id] = MatchedPattern(
                pattern_id=match.rule_id,
                name=match.name,
                category=match.category,
                explanation=match.explanation,
                evidence=[evidence],
            )
        else:
            existing.evidence.append(evidence)

    matched_patterns = list(patterns_by_id.values())
    return AnalyzeEmailResponse(
        classification=(
            Classification.SUSPICIOUS
            if result.matched
            else Classification.NO_CONFIGURED_PATTERNS_MATCHED
        ),
        # This educational score counts rule types; it is not a probability.
        risk_score=min(100, len(matched_patterns) * 20),
        mode=AnalysisMode.REGEX,
        regex_result=RegexAnalysisResult(
            matched=result.matched,
            matched_patterns=matched_patterns,
            explanation=(
                f"Matched {len(matched_patterns)} configured regex rule(s). "
                "Matches are indicators for review, not proof of phishing."
                if result.matched
                else (
                    "No configured regex rule matched. This does not guarantee "
                    "that the email is safe."
                )
            ),
        ),
    )
