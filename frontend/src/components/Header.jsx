import React from "react";
import { Menu, RefreshCw } from "lucide-react";
function Header({ title, onOpenSidebar, isConnected, isChecking, onCheckConnection }) {
  return <header className="topbar"><div className="row"><button className="btn compact mobile-only" onClick={onOpenSidebar} aria-label="Open navigation menu"><Menu size={18} /></button><div className="topbar-title"><span>Workspace / </span><strong>{title}</strong></div></div><button className={`status ${isConnected ? "connected" : ""}`} onClick={onCheckConnection} disabled={isChecking} aria-label="Refresh backend connection status"><span className="dot" />{isChecking ? "Checking backend…" : isConnected ? "Backend: Connected" : "Backend: Offline"}<RefreshCw size={12} /></button></header>;
}
export {
  Header as default
};
