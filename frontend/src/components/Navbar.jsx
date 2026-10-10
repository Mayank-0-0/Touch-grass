import React from "react";
import AIStatusBanner from "./AIStatusBanner";

export default function Navbar({ activeTab, setActiveTab, aiStatus, onRefreshAI }) {
  return (
    <header className="topbar">
      <div className="topbar-left" onClick={() => setActiveTab("dashboard")} style={{ cursor: "pointer" }}>
        <div className="brand-mark" aria-hidden="true">🌱</div>
        <div className="brand-copy">
          <strong>Touch Grass</strong>
          <span>AI-Powered Offline Activity Companion</span>
        </div>
      </div>

      <div className="topbar-right">
        <AIStatusBanner aiStatus={aiStatus} onRefresh={onRefreshAI} />
      </div>
    </header>
  );
}
