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
function ClosureStudio() {
  const [state, setState] = useState("s0"), [source, setSource] = useState(null), [sourceError, setSourceError] = useState(null);
  const job = useJob(), r = job.result, play = usePlayback(r?.steps.length || 0), step = r?.steps[play.index];
  useEffect(() => {
    let alive = true;
    defaultNfa().then((m) => {
      if (alive) setSource(m);
    }).catch((e) => {
      if (alive) setSourceError(e);
    });
    return () => {
      alive = false;
    };
  }, []);
  return <div className="stack"><Panel title="ε-closure explorer"><div className="stack"><p className="small muted">Follow only epsilon edges of the same configured email ε-NFA. Closure includes the seed itself and consumes no input symbol.</p><div><label htmlFor="closure-state">Selected state</label><select id="closure-state" className="input" value={state} disabled={job.loading || !source} onChange={(e) => {
    setState(e.target.value);
    job.clear();
  }}>{(source?.states || ["s0"]).map((s) => <option key={s}>{s}</option>)}</select></div><button className="btn primary" disabled={job.loading || !source} onClick={() => {
    play.reset();
    job.run(() => labRequest("closure", { state }));
  }}>{job.loading ? "Expanding…" : "Explore epsilon closure"}</button><ErrorNotice error={job.error || sourceError} /></div></Panel>{r && <><section className="panel"><StepControls playback={play} label="Epsilon expansion step" /><div className="panel-body stack"><div className="grid3"><Metric label="Selected seed">{state}</Metric><Metric label="Newly discovered">{setLabel(step.newly_discovered)}</Metric><Metric label="Current closure">{setLabel(step.closure)}</Metric></div><p className="small">{step.source ? `${step.source} —ε→ ${step.target}. ` : ""}{step.explanation}</p>{play.index === play.last && <p className="accent small">Final ε-closure({state}) = {setLabel(r.closure)}</p>}</div></section><AutomataGraph model={r.model} activeStates={step.closure} activeEdges={step.source ? [edgeKey(step.source, null, step.target)] : []} title="Closure expansion · actual epsilon edges" /><Panel title="Expansion trace"><div className="table-wrap"><table><thead><tr><th>Step</th><th>Edge</th><th>New states</th><th>Closure</th></tr></thead><tbody>{r.steps.slice(0, play.index + 1).map((s, i) => <tr key={i} className={i === play.index ? "current" : ""}><td>{i}</td><td>{s.source ? `${s.source} —ε→ ${s.target}` : "seed"}</td><td>{setLabel(s.newly_discovered)}</td><td>{setLabel(s.closure)}</td></tr>)}</tbody></table></div></Panel></>}</div>;
}
export {
  ClosureStudio as default
};
