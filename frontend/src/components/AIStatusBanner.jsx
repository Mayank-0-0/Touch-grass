import React from "react";

export default function AIStatusBanner({ aiStatus, onRefresh }) {
  if (!aiStatus) return null;

  return (
    <div className={`ai-status-pill ${aiStatus.online ? "online" : "offline"}`}>
      <span className="ai-status-dot" aria-hidden="true" />
      <span className="ai-status-text">
        {aiStatus.online ? (
          <>Local Gemma Connected (llama.cpp)</>
        ) : (
          <>Offline Mode (Curated Fallbacks Active)</>
        )}
      </span>
      <button
        className="ai-refresh-btn"
        title="Check local AI server connectivity"
        onClick={onRefresh}
      >
        ↻
      </button>
    </div>
  );
}
