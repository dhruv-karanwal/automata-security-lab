import React, { useEffect, useState } from "react";
import { convertNfaToDfa, getAutomaton } from "../services/api.js";
import { Panel, ErrorNotice, Metric, setLabel } from "./ui.jsx";
import AutomataGraph from "./AutomataGraph.jsx";
import TransitionTable from "./TransitionTable.jsx";
import StepControls, { usePlayback } from "./StepControls.jsx";
import { convertedModel, edgeKey } from "../utils/traceModel.js";
function NfaToDfaConversion() {
  const [result, setResult] = useState(null), [source, setSource] = useState(null), [error, setError] = useState(null), [loading, setLoading] = useState(false);
  const play = usePlayback((result?.construction_steps.length || 0) + 1);
  useEffect(() => {
    let alive = true;
    getAutomaton("nfa_phishing_branches").then((r) => {
      if (alive) setSource(r);
    }).catch((e) => {
      if (alive) setError(e);
    });
    return () => {
      alive = false;
    };
  }, []);
  async function run() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await convertNfaToDfa("nfa_phishing_branches"));
      play.reset();
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }
  const step = result?.construction_steps[play.index - 1], steps = result?.construction_steps.slice(0, play.index) || [];
  const discovered = new Set(result ? [result.dfa_start_state, ...steps.map((s) => s.target_state)] : []);
  const model = result ? { ...convertedModel(result), states: result.dfa_states.filter((s) => discovered.has(s.state_id)).map((s) => s.state_id), accepting_states: result.dfa_accepting_states.filter((s) => discovered.has(s)), transitions: steps.map((s) => ({ from_state: s.source_state, symbol: s.symbol, to_states: [s.target_state] })) } : null;
  return <div className="stack"><Panel title="NFA → DFA · subset construction" aside={<button className="btn primary" onClick={run} disabled={loading || !source}>{loading ? "Constructing…" : "Generate equivalent DFA"}</button>}><p className="small muted">Explore the email recognizer’s reachable subsets. Each step computes move(T, symbol), then ε-closure. This does not analyze or modify an email.</p><ErrorNotice error={error} /></Panel>{result && <><section className="panel"><StepControls playback={play} label="Subset construction step" /><div className="panel-body stack"><div className="grid3"><Metric label="Initial ε-closure">{setLabel(result.initial_epsilon_closure)}</Metric><Metric label="Subsets discovered">{discovered.size} / {result.dfa_states.length}</Metric><Metric label="Transitions explored">{play.index} / {result.transitions.length}</Metric></div><div className="notice">{step ? <><code>{step.source_state}</code> on <code>{step.symbol}</code>: move = {setLabel(step.move_result)}; ε-closure = {setLabel(step.epsilon_closure)} → <strong>{step.target_state}</strong>. {step.created_new_state ? "New subset discovered." : "Existing subset reused."}</> : <>Start at {setLabel(result.initial_epsilon_closure)} = {result.dfa_start_state}.</>}</div><div className="row">{result.dfa_states.filter((s) => discovered.has(s.state_id)).map((s) => <span className={`tag ${s.is_accepting ? "teal" : ""}`} key={s.state_id}>{s.state_id} = {setLabel(s.nfa_states)}{s.is_accepting ? " ◎" : ""}</span>)}</div></div></section><div className="grid2"><AutomataGraph model={source} activeStates={step?.source_nfa_states || result.initial_epsilon_closure} title="Source · three-phrase ε-NFA" /><AutomataGraph model={model} activeStates={step ? [step.target_state] : [result.dfa_start_state]} activeEdges={step ? [edgeKey(step.source_state, step.symbol, step.target_state)] : []} title="Generated DFA · discovered so far" /></div><Panel title={play.index === play.last ? "Complete generated transition table" : "Transition table · explored so far"}><TransitionTable model={model} activeEdges={step ? [edgeKey(step.source_state, step.symbol, step.target_state)] : []} /><p className="tiny muted">An ∅ cell during construction is unexplored. At completion, D_dead is the empty subset and the function is total.</p></Panel></>}</div>;
}
export {
  NfaToDfaConversion as default
};
