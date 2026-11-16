import React from "react";
import { setLabel } from "./ui.jsx";
function ExecutionTraceView({ trace = [], isAccepted, title = "Execution trace", currentIndex, onSelect }) {
  return <div><div className="row between" style={{ margin: "12px 0" }}><h3>{title}</h3><span className="tag">Final result: {isAccepted ? "accepted" : "rejected"}</span></div><div className="table-wrap"><table><thead><tr><th>Step</th><th>Consumed</th><th>State / active set</th><th>Explanation</th></tr></thead><tbody>{trace.map((row, i) => <tr key={i} className={i === currentIndex ? "current" : ""} aria-current={i === currentIndex ? "step" : void 0}><td>{onSelect ? <button className="btn compact" aria-label={`Go to step ${i}`} onClick={() => onSelect(i)}>{row.step}</button> : row.step}</td><td>{row.symbol ?? row.consumedToken ?? "ε / initial"}</td><td className="mono">{row.state || setLabel(row.states_after || row.activeStates || [])}</td><td style={{ whiteSpace: "normal", minWidth: 200 }}>{row.explanation || row.action}</td></tr>)}</tbody></table></div></div>;
}
export {
  ExecutionTraceView as default
};
