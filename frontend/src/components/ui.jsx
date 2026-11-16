import React from "react";
function Panel({ title, aside, children, className = "" }) {
  return <section className={`panel ${className}`}>{title && <div className="panel-head"><h2>{title}</h2>{aside}</div>}<div className="panel-body">{children}</div></section>;
}
function PageIntro({ eyebrow, title, children, tag }) {
  return <div className="page-intro"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{children}</p></div>{tag && <span className="tag">{tag}</span>}</div>;
}
function ErrorNotice({ error }) {
  return error ? <div className="error" role="alert">{error.message || String(error)}</div> : null;
}
function Metric({ label, children }) {
  return <div className="metric"><span className="tiny muted">{label}</span><strong>{children}</strong></div>;
}
const setLabel = (states = []) => states.length ? `{ ${states.join(", ")} }` : "∅";
export {
  ErrorNotice,
  Metric,
  PageIntro,
  Panel,
  setLabel
};
