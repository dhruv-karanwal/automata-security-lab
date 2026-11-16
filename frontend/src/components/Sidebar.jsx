import React from "react";
import { NavLink } from "react-router-dom";
import { MailSearch, Workflow, FlaskConical, BookOpen, ShieldCheck, X, LockKeyhole } from "lucide-react";
const items = [["/", "Analyze Email", MailSearch], ["/engine", "Detection Engine", Workflow], ["/lab", "Automata Lab", FlaskConical], ["/theory", "Theory & Viva", BookOpen]];
function Sidebar({ isOpen, onClose }) {
  return <>{isOpen && <button className="mobile-backdrop" aria-label="Close navigation overlay" onClick={onClose} />}<aside className={`sidebar ${isOpen ? "open" : ""}`} aria-label="Main navigation" onKeyDown={(e) => {
    if (e.key === "Escape") onClose();
  }}><div className="brand"><div className="brand-icon"><ShieldCheck size={22} /></div><div><strong>Automata<br />Security Lab</strong><small>Email pattern analysis</small></div><button className="btn compact mobile-only" aria-label="Close navigation" onClick={onClose}><X size={16} /></button></div><div className="nav-label">Workspace</div><nav>{items.map(([to, label, Icon]) => <NavLink key={to} to={to} end={to === "/"} onClick={onClose} className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}><Icon size={18} />{label}</NavLink>)}</nav><div className="sidebar-foot"><LockKeyhole size={17} className="accent" /><strong>Local by design</strong>Your email stays on this computer. No external analysis services.<div className="divider" style={{ margin: "18px 0 12px" }} />Automata Theory · Course project</div></aside></>;
}
export {
  Sidebar as default
};
