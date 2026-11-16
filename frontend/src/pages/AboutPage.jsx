import React from "react";
import { PageIntro, Panel } from "../components/ui.jsx";
function AboutPage() {
  return <div className="page reading"><PageIntro eyebrow="Scope & privacy" title="A transparent academic demonstrator.">Local email-pattern recognition using real finite automata and configured regular expressions.</PageIntro><Panel title="Know the limits"><ul><li>Whole-input automata and substring regex rules recognize only configured patterns.</li><li>No match does not guarantee safety; a match does not prove phishing.</li><li>The risk score is an educational heuristic, not a probability.</li><li>PDF uploads are bounded to 10 MB. OCR, scanned PDFs, attachments and mailbox integration are outside scope.</li><li>No permanent email storage or external analysis services. Multipart processing may use temporary OS spooling.</li></ul></Panel></div>;
}
export {
  AboutPage as default
};
