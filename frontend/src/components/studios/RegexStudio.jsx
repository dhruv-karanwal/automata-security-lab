import React, { useState, useEffect } from "react";
import { Panel, ErrorNotice, Metric, setLabel } from "../ui.jsx";
import AutomataGraph from "../AutomataGraph.jsx";
import TransitionTable from "../TransitionTable.jsx";
import ExecutionTraceView from "../ExecutionTraceView.jsx";
import StepControls, { usePlayback } from "../StepControls.jsx";
import { traceFrame, edgeKey } from "../../utils/traceModel.js";
import { labRequest, getAutomaton } from "../../services/api.js";
import { useJob } from "../../hooks/useJob.js";
const defaultNfa = () => getAutomaton("nfa_phishing_branches");
function RegexStudio() {
  const [expression, setExpression] = useState("WIN|CLAIM"), [input, setInput] = useState("CLAIM"), [view, setView] = useState("construction");
  const job = useJob(), r = job.result;
  const build = usePlayback(r?.fragments.length || 0), sim = usePlayback(r?.simulation.trace.length || 0);
  const frag = r?.fragments[build.index];
  const model = r ? view === "simulation" ? r.model : { ...r.model, states: frag.states, start_state: frag.start_state, accepting_states: [frag.accepting_state], transitions: frag.transitions } : null;
  const frame = r ? traceFrame(r.model, r.simulation.trace, sim.index) : null;
  return <div className="stack"><Panel title="Regex → ε-NFA · Thompson’s construction"><div className="stack"><div className="notice">A separate, case-sensitive character grammar for email phrase fragments. It does not convert or replace the six Python regex detection rules. Whitespace in the expression is ignored; whitespace in example input is literal.</div><div className="grid2"><div><label htmlFor="regex-expression">Expression</label><input id="regex-expression" className="input mono" value={expression} maxLength={128} disabled={job.loading} onChange={(e) => {
    setExpression(e.target.value);
    job.clear();
  }} /></div><div><label htmlFor="regex-input">Example string (empty allowed)</label><input id="regex-input" className="input mono" value={input} maxLength={256} disabled={job.loading} onChange={(e) => {
    setInput(e.target.value);
    job.clear();
  }} /></div></div><p className="tiny muted">Literals: ASCII letters, digits, _ @ . ! : / - · concatenation · union | · star * · parentheses. Precedence: * then concatenation then |. No classes, +, ?, escapes, or anchors. At most 64 expression characters and 32 distinct literals.</p><button className="btn primary" disabled={job.loading} onClick={() => {
    build.reset();
    sim.reset();
    job.run(() => labRequest("thompson", { expression, input_text: input }));
  }}>{job.loading ? "Constructing…" : "Build & simulate expression"}</button><ErrorNotice error={job.error} /></div></Panel>{r && <><div className="tabs">{["construction", "simulation"].map((v) => <button key={v} className={`btn ${view === v ? "selected" : ""}`} aria-pressed={view === v} onClick={() => {
    build.setPlaying(false);
    sim.setPlaying(false);
    setView(v);
  }}>{v === "construction" ? "Construction fragments" : "Simulate generated ε-NFA"}</button>)}</div><section className="panel"><StepControls playback={view === "construction" ? build : sim} label={view === "construction" ? "Thompson construction step" : "Generated NFA execution step"} /><div className="panel-body"><div className="notice">{view === "construction" ? frag.explanation : frame.explanation}</div>{view === "construction" ? <div className="row tiny muted" style={{ marginTop: 12 }}>Created states: {setLabel(frag.created_states)} · Created edges: {frag.created_transitions.map((t) => `${t.from_state} —${t.symbol ?? "ε"}→ ${t.to_states.join(", ")}`).join("; ")}</div> : <><div className="grid3" style={{ marginTop: 14 }}><Metric label="Active states">{setLabel(frame.active)}</Metric><Metric label="Input position">{sim.index} / {Array.from(input).length}</Metric><Metric label="Remaining input">{frame.remaining.join("") || "ε"}</Metric></div>{sim.index === sim.last && <p className="accent small" style={{ marginTop: 12 }}>Final result: {r.simulation.accepted ? "accepted" : "rejected"}. This is expression membership, not an email security verdict.</p>}</>}</div></section><AutomataGraph model={model} activeStates={view === "simulation" ? frame.active : [frag.start_state, frag.accepting_state]} activeEdges={view === "simulation" ? frame.edges : frag.created_transitions.flatMap((t) => t.to_states.map((to) => edgeKey(t.from_state, t.symbol, to)))} title={view === "simulation" ? "Computed Thompson ε-NFA" : "Intermediate fragment graph"} /><Panel title="Constructed transition relation"><TransitionTable model={model} /><details style={{ marginTop: 16 }}><summary>Parsed syntax tree</summary><pre className="tiny">{JSON.stringify(r.syntax_tree, null, 2)}</pre></details>{view === "simulation" && <ExecutionTraceView trace={r.simulation.trace} isAccepted={r.simulation.accepted} currentIndex={sim.index} onSelect={(i) => {
    sim.setPlaying(false);
    sim.setIndex(i);
  }} />}</Panel></>}</div>;
}
export {
  RegexStudio as default
};
