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
function MinimizeStudio() {
  const job = useJob(), r = job.result, play = usePlayback(r?.steps.length || 0);
  const step = r?.steps[play.index];
  return <div className="stack"><Panel title="DFA minimization · partition refinement" aside={<button className="btn primary" disabled={job.loading} onClick={() => {
    play.reset();
    job.run(() => labRequest("minimize", {}));
  }}>{job.loading ? "Refining…" : "Minimize email recognizer"}</button>}><p className="small muted">Determinize the configured three-phrase ε-NFA, complete missing transitions with a sink, remove unreachable states, and refine accepting/non-accepting partitions until stable.</p><ErrorNotice error={job.error} /></Panel>{r && <><section className="panel"><StepControls playback={play} label="Partition refinement step" /><div className="panel-body stack"><div className="notice">{step.explanation}</div><div className="row">{step.partitions.map((p, i) => <span className="tag purple" key={i}>P{i}: {setLabel(p)}</span>)}</div>{step.splits.map((s, i) => <div key={i} className="small"><strong>Split {setLabel(s.block)}</strong><div className="row">{s.groups.map((g, j) => <span key={j} className="tag">{setLabel(g.states)} → [{g.signature.join(", ")}]</span>)}</div><p className="tiny muted">Destination-partition signatures in alphabet order: {r.total_model.alphabet.join(", ")}. Different signatures cannot remain in the same block.</p></div>)}<div className="grid3"><Metric label="Reachable total DFA states">{r.before_count}</Metric><Metric label="Current partition blocks">{step.partitions.length}</Metric><Metric label="Removed unreachable states">{setLabel(r.removed_unreachable)}</Metric></div></div></section><AutomataGraph model={r.total_model} activeStates={step.splits.flatMap((s) => s.block)} title="Before · reachable total DFA" />{play.index === play.last && <><Panel title="Stable equivalence classes"><div className="row">{r.classes.map((c) => <span className="tag teal" key={c.state}>{c.state} = {setLabel(c.members)}</span>)}</div><p className="small muted" style={{ marginTop: 12 }}>{r.before_count} → {r.after_count} states. This preserves the entire token language, not only sample phrases.</p></Panel><AutomataGraph model={r.model} title="After · minimized email-pattern DFA" /><Panel title="Minimized transition table"><TransitionTable model={r.model} /></Panel></>}</>}</div>;
}
export {
  MinimizeStudio as default
};
