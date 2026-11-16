import React from "react";
import { useSearchParams } from "react-router-dom";
import { PageIntro } from "../components/ui.jsx";
import NfaToDfaConversion from "../components/NfaToDfaConversion.jsx";
import RegexStudio from "../components/studios/RegexStudio.jsx";
import MinimizeStudio from "../components/studios/MinimizeStudio.jsx";
import EquivalenceStudio from "../components/studios/EquivalenceStudio.jsx";
import ClosureStudio from "../components/studios/ClosureStudio.jsx";
const tabs = [["subset", "NFA → DFA"], ["regex", "Regex → ε-NFA"], ["minimize", "Minimization"], ["equivalence", "Equivalence"], ["closure", "ε-closure"]];
function TeachingLabPage() {
  const [params, setParams] = useSearchParams();
  const tab = tabs.some(([id]) => id === params.get("tool")) ? params.get("tool") : "subset";
  return <div className="page"><PageIntro eyebrow="Automata lab" title="Open the engine. Explore the theory." tag="Computed algorithms">Build, transform, and compare automata using the project’s email phrases and simple email-related expressions. These operations do not change the detection rules.</PageIntro><div className="tabs" aria-label="Algorithm workspace">{tabs.map(([id, label]) => <button className={`btn ${tab === id ? "selected" : ""}`} aria-pressed={tab === id} key={id} onClick={() => setParams({ tool: id })}>{label}</button>)}</div>{tab === "subset" ? <NfaToDfaConversion /> : tab === "regex" ? <RegexStudio /> : tab === "minimize" ? <MinimizeStudio /> : tab === "equivalence" ? <EquivalenceStudio /> : <ClosureStudio />}</div>;
}
export {
  TeachingLabPage as default
};
