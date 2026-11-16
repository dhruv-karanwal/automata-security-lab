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
function EquivalenceStudio() {
  const [type, setType] = useState("minimized"), [leftExpression, setLeft] = useState("WIN"), [rightExpression, setRight] = useState("WIN|CLAIM");
  const job = useJob(), r = job.result, play = usePlayback(r?.exploration.length || 0), pair = r?.exploration[play.index];
  async function compare() {
    let left, right;
    if (type === "expressions") {
      left = (await labRequest("thompson", { expression: leftExpression })).model;
      right = (await labRequest("thompson", { expression: rightExpression })).model;
    } else if (type === "detectors") {
      left = await getAutomaton("dfa_win_prize_now");
      right = await defaultNfa();
    } else {
      left = await defaultNfa();
      right = (await labRequest("minimize", {})).model;
    }
    return labRequest("equivalence", { left, right });
  }
  return <div className="stack"><Panel title="Exact language equivalence"><div className="stack"><label htmlFor="comparison">Automata to compare</label><select id="comparison" className="input" value={type} disabled={job.loading} onChange={(e) => {
    setType(e.target.value);
    job.clear();
  }}><option value="minimized">Three-phrase ε-NFA vs its minimized DFA</option><option value="detectors">WIN PRIZE NOW DFA vs three-phrase ε-NFA</option><option value="expressions">Two email-fragment Thompson expressions</option></select>{type === "expressions" && <div className="grid2"><div><label htmlFor="left-expression">Left expression</label><input id="left-expression" className="input mono" disabled={job.loading} value={leftExpression} maxLength={128} onChange={(e) => {
    setLeft(e.target.value);
    job.clear();
  }} /></div><div><label htmlFor="right-expression">Right expression</label><input id="right-expression" className="input mono" disabled={job.loading} value={rightExpression} maxLength={128} onChange={(e) => {
    setRight(e.target.value);
    job.clear();
  }} /></div></div>}<p className="small muted">ε-NFAs are determinized first. Breadth-first product exploration checks acceptance disagreement over the union alphabet. Missing transitions enter an implicit rejecting sink (⊥). No bounded sampling is used.</p><button className="btn primary" disabled={job.loading} onClick={() => {
    play.reset();
    job.run(compare);
  }}>{job.loading ? "Exploring product…" : "Compare languages exactly"}</button><ErrorNotice error={job.error} /></div></Panel>{r && <><section className="panel"><StepControls playback={play} label="Product exploration step" /><div className="panel-body stack"><div className="grid2"><Metric label="Current left state">{pair.left ?? "⊥"} {pair.left_accepting ? "◎" : ""}</Metric><Metric label="Current right state">{pair.right ?? "⊥"} {pair.right_accepting ? "◎" : ""}</Metric></div><p className="tiny muted">Explored {play.index + 1} of {r.exploration.length} reachable product pairs{pair.distinguishing ? " · acceptance disagreement found" : ""}.</p>{play.index === play.last && <div className="notice"><h3>{r.equivalent ? "Equivalent languages" : "Not equivalent"}</h3><p>{r.equivalent ? "The finite reachable product is exhausted without acceptance disagreement." : <>Shortest distinguishing input: <code>{r.witness.length ? r.witness.join(type === "expressions" ? "" : " ") : "ε (empty string)"}</code></>}</p>{!r.equivalent && <div className="mono tiny" style={{ marginTop: 10 }}>Left path: {r.path.map((p) => p.left ?? "⊥").join(" → ")}<br />Right path: {r.path.map((p) => p.right ?? "⊥").join(" → ")}</div>}</div>}</div></section><div className="grid2"><AutomataGraph model={r.left} activeStates={pair.left ? [pair.left] : []} title="Left · deterministic representation" /><AutomataGraph model={r.right} activeStates={pair.right ? [pair.right] : []} title="Right · deterministic representation" /></div><Panel title="Product-state exploration"><div className="table-wrap"><table><thead><tr><th>Pair</th><th>Left</th><th>Right</th><th>Acceptance comparison</th></tr></thead><tbody>{r.exploration.slice(0, play.index + 1).map((p, i) => <tr key={i} className={i === play.index ? "current" : ""}><td>{i}</td><td>{p.left ?? "⊥"}</td><td>{p.right ?? "⊥"}</td><td>{p.distinguishing ? "Different" : p.left_accepting ? "Both accepting" : "Both non-accepting"}</td></tr>)}</tbody></table></div></Panel></>}</div>;
}
export {
  EquivalenceStudio as default
};
