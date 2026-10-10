import React from "react";

export default function ResultsView({
  challenge,
  evaluationResult,
  onStartAnother,
  onGoToDashboard,
  onGoToHistory,
}) {
  const score = evaluationResult?.score ?? challenge?.score ?? 0;
  const feedback = evaluationResult?.feedback || challenge?.feedback || "Great job completing your offline session!";

  let evalDetails = {};
  if (challenge?.evaluation_details) {
    if (typeof challenge.evaluation_details === "object") {
      evalDetails = challenge.evaluation_details;
    } else {
      try {
        evalDetails = JSON.parse(challenge.evaluation_details);
      } catch (e) {
        evalDetails = {};
      }
    }
  }

  const relevance = evaluationResult?.relevance || evalDetails?.relevance || "Directly aligned with challenge goals.";
  const quality = evaluationResult?.quality || evalDetails?.quality || "Observant sensory details provided.";
  const completionScore = evaluationResult?.completion_score || evalDetails?.completion_score || score;
  const streak = evaluationResult?.current_streak;

  return (
    <div className="results-view">
      {/* Celebration Header */}
      <div className="results-hero">
        <span className="results-trophy" aria-hidden="true">🎉</span>
        <h2>Challenge Completed!</h2>
        <p>You successfully stepped away from screens and completed your activity.</p>
      </div>

      {/* Score and Streak Spotlight */}
      <div className="results-spotlight-grid">
        <div className="score-card">
          <span className="spotlight-label">Activity Score</span>
          <div className="score-ring">
            <span className="score-number">{score}</span>
            <span className="score-denominator">/ 100</span>
          </div>
          <span className="score-grade-tag">
            {score >= 90 ? "🌿 Outstanding Offline Presence" : score >= 75 ? "🌱 Solid Offline Engagement" : "🍃 Activity Completed"}
          </span>
        </div>

        {streak !== undefined && (
          <div className="streak-celebration-card">
            <span className="spotlight-label">Streak Status</span>
            <div className="streak-flame-display">
              <span className="flame-icon">🔥</span>
              <span className="streak-days">{streak} {streak === 1 ? "Day" : "Days"}</span>
            </div>
            <p className="streak-note">Keep up the daily offline momentum!</p>
          </div>
        )}
      </div>

      {/* AI Evaluation Breakdown */}
      <div className="evaluation-details-card">
        <h3>Local AI Evaluation Breakdown</h3>

        <div className="feedback-quote-box">
          <span className="quote-icon">“</span>
          <p className="feedback-text">{feedback}</p>
        </div>

        <div className="rubric-metrics-grid">
          <div className="metric-box">
            <span className="metric-title">Activity Relevance</span>
            <p className="metric-desc">{relevance}</p>
          </div>

          <div className="metric-box">
            <span className="metric-title">Observation & Evidence Quality</span>
            <p className="metric-desc">{quality}</p>
          </div>

          <div className="metric-box">
            <span className="metric-title">Task Completion</span>
            <div className="completion-bar-wrap">
              <div className="completion-bar" style={{ width: `${completionScore}%` }} />
            </div>
            <span className="metric-score-label">{completionScore}% complete</span>
          </div>
        </div>
      </div>

      {/* Navigation Actions */}
      <div className="results-actions">
        <button
          type="button"
          className="secondary-button"
          onClick={onGoToDashboard}
        >
          Return to Dashboard
        </button>

        <button
          type="button"
          className="secondary-button"
          onClick={onGoToHistory}
        >
          View in History
        </button>

        <button
          type="button"
          className="primary-button"
          onClick={onStartAnother}
        >
          <span>✦</span> Start Another Challenge
        </button>
      </div>
    </div>
  );
}
