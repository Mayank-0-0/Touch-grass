import React, { useState } from "react";

export default function HistoryView({ history, onStartNew }) {
  const [expandedId, setExpandedId] = useState(null);
  const [filterInterest, setFilterInterest] = useState("all");

  const interestsList = Array.from(
    new Set((history || []).map((item) => item.interest).filter(Boolean))
  );

  const filteredHistory = (history || []).filter((item) => {
    if (filterInterest === "all") return true;
    return item.interest === filterInterest;
  });

  function toggleExpand(id) {
    setExpandedId(expandedId === id ? null : id);
  }

  return (
    <div className="history-view">
      <div className="history-header-row">
        <div className="section-heading">
          <h2>Offline Activity History</h2>
          <p>Review your past screenless achievements, scores, and observational reflections.</p>
        </div>

        {interestsList.length > 0 && (
          <div className="history-filter-wrap">
            <label htmlFor="filter-interest" className="filter-label">Filter:</label>
            <select
              id="filter-interest"
              className="filter-select"
              value={filterInterest}
              onChange={(e) => setFilterInterest(e.target.value)}
            >
              <option value="all">All Interests</option>
              {interestsList.map((interest) => (
                <option key={interest} value={interest}>
                  {interest}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {!history || history.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon" aria-hidden="true">📖</span>
          <strong>No completed activities yet</strong>
          <p>Complete your first challenge to see your score and history recorded here!</p>
          <div style={{ marginTop: "16px" }}>
            <button className="primary-button" onClick={onStartNew}>
              <span>✦</span> Start Your First Challenge
            </button>
          </div>
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon" aria-hidden="true">🔍</span>
          <strong>No activities match "{filterInterest}"</strong>
          <p>Try switching the filter to all interests.</p>
        </div>
      ) : (
        <div className="history-list">
          {filteredHistory.map((item) => {
            const isExpanded = expandedId === item.id;
            const completedDate = item.submitted_at
              ? new Date(item.submitted_at).toLocaleDateString(undefined, {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })
              : "Completed";

            return (
              <article
                className={`history-card ${isExpanded ? "expanded" : ""}`}
                key={item.id}
              >
                <div
                  className="history-card-header"
                  onClick={() => toggleExpand(item.id)}
                  style={{ cursor: "pointer" }}
                >
                  <div className="history-main-info">
                    <div className="history-badges">
                      <span className="recent-interest-badge">{item.interest}</span>
                      <span className="meta-chip duration-chip-static">⏱ {item.duration_minutes} min</span>
                      <span className="history-date-text">{completedDate}</span>
                    </div>
                    <h3 className="history-title">{item.title}</h3>
                  </div>

                  <div className="history-card-right">
                    <div className="score-badge-circle">
                      <span className="score-value-bold">{item.score}</span>
                      <span className="score-scale">/100</span>
                    </div>
                    <span className="expand-indicator" aria-hidden="true">
                      {isExpanded ? "▲" : "▼"}
                    </span>
                  </div>
                </div>

                {/* Collapsible Details */}
                {isExpanded && (
                  <div className="history-card-body">
                    {item.feedback && (
                      <div className="history-feedback-box">
                        <strong>AI Evaluation Feedback:</strong>
                        <p>"{item.feedback}"</p>
                      </div>
                    )}

                    <div className="history-instructions-box">
                      <strong>Activity Assigned:</strong>
                      <p>{item.instructions}</p>
                    </div>

                    {/* Submitted Proof */}
                    {item.proof_answers && (
                      <div className="history-proof-box">
                        <strong>Submitted Reflections:</strong>
                        {typeof item.proof_answers === "object" ? (
                          <div className="proof-qa-list">
                            {Object.entries(item.proof_answers).map(([q, a], idx) => (
                              <div key={idx} className="proof-qa-item">
                                <span className="qa-question">Q: {q}</span>
                                <p className="qa-answer">A: {a || "(No answer recorded)"}</p>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="qa-answer">{item.proof_answers}</p>
                        )}
                      </div>
                    )}

                    {/* Uploaded Photo */}
                    {item.proof_image && (
                      <div className="history-photo-box">
                        <strong>Attached Proof Photo:</strong>
                        <img
                          src={item.proof_image}
                          alt="Proof evidence"
                          className="history-proof-image"
                        />
                      </div>
                    )}
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}
