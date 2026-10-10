import React, { useState, useEffect } from "react";

function parseTargetTime(targetEndAt) {
  if (!targetEndAt) return null;
  let str = String(targetEndAt).trim();
  // Ensure ISO string is treated as UTC if it lacks a timezone designator
  if (!str.endsWith("Z") && !str.includes("+") && !/[+-]\d{2}:\d{2}$/.test(str)) {
    str += "Z";
  }
  const time = new Date(str).getTime();
  return isNaN(time) ? null : time;
}

export default function ChallengeMode({
  challenge,
  onProceedToProof,
  onAbandon,
}) {
  const getInitialRemaining = () => {
    if (typeof challenge.remaining_seconds === "number" && challenge.remaining_seconds > 0) {
      return challenge.remaining_seconds;
    }
    const targetTime = parseTargetTime(challenge.target_end_at);
    if (targetTime) {
      const diff = Math.floor((targetTime - Date.now()) / 1000);
      if (diff > 0) return diff;
    }
    return Math.round((challenge.duration_minutes || 30) * 60);
  };

  const [remainingSeconds, setRemainingSeconds] = useState(getInitialRemaining);
  const [confirmAbandon, setConfirmAbandon] = useState(false);

  // Recalculate remaining seconds every second from target_end_at timestamp
  useEffect(() => {
    function calculateRemaining() {
      const targetTime = parseTargetTime(challenge.target_end_at);
      if (!targetTime) {
        return typeof challenge.remaining_seconds === "number" && challenge.remaining_seconds > 0
          ? challenge.remaining_seconds
          : Math.round((challenge.duration_minutes || 30) * 60);
      }
      const now = Date.now();
      const diff = Math.floor((targetTime - now) / 1000);
      return Math.max(0, diff);
    }

    setRemainingSeconds(calculateRemaining());

    const interval = setInterval(() => {
      setRemainingSeconds(calculateRemaining());
    }, 1000);

    return () => clearInterval(interval);
  }, [challenge.target_end_at, challenge.duration_minutes, challenge.remaining_seconds]);

  const totalSeconds = Math.max(1, challenge.duration_minutes * 60);
  const elapsedPercent = Math.min(100, Math.max(0, ((totalSeconds - remainingSeconds) / totalSeconds) * 100));

  const hours = Math.floor(remainingSeconds / 3600);
  const minutes = Math.floor((remainingSeconds % 3600) / 60);
  const seconds = remainingSeconds % 60;
  const isTimeUp = remainingSeconds === 0;

  const formattedTime =
    hours > 0
      ? `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`
      : `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

  return (
    <div className="challenge-mode-view">
      {/* Serene Focus Header */}
      <div className="focus-header">
        <div className="focus-leaf-badge">🍃 Focus Mode Active</div>
        <h2>{challenge.title}</h2>
        <p className="focus-sub">Category: {challenge.interest} • Total: {challenge.duration_minutes} minutes</p>
      </div>

      {/* Large Focus Timer Readout */}
      <div className={`focus-timer-card ${isTimeUp ? "time-up" : ""}`}>
        <div className="timer-display-box">
          <span className="timer-digits" role="timer" aria-label={`${minutes} minutes ${seconds} seconds remaining`}>
            {formattedTime}
          </span>
          <span className="timer-status-caption">
            {isTimeUp ? "Time's up! Welcome back." : "Time remaining in your offline session"}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="timer-progress-track">
          <div
            className="timer-progress-bar"
            style={{ width: `${elapsedPercent}%` }}
          />
        </div>

        {/* Prompt to leave screen */}
        {!isTimeUp ? (
          <div className="step-away-reminder">
            <span className="reminder-icon">🌱</span>
            <div className="reminder-text">
              <strong>Leave your computer or phone here</strong>
              <p>Step away into the real world. Your progress is saved safely. When you finish, come back to submit your proof.</p>
            </div>
          </div>
        ) : (
          <div className="completion-announcement">
            <span className="announcement-icon">🎉</span>
            <div className="announcement-text">
              <strong>Congratulations on completing your screenless session!</strong>
              <p>Take a breath and submit your reflection answers to earn your score and continue your streak.</p>
            </div>
          </div>
        )}
      </div>

      {/* Quick Reference Instructions */}
      <div className="instructions-reference-card">
        <h3>Activity Instructions Reference</h3>
        <p>{challenge.instructions}</p>
        {challenge.expected_result && (
          <p className="ref-expected"><strong>Goal:</strong> {challenge.expected_result}</p>
        )}
      </div>

      {/* Focus Mode Navigation Actions */}
      <div className="focus-actions-bar">
        <button
          type="button"
          className="abandon-btn"
          onClick={() => setConfirmAbandon(true)}
        >
          Abandon Challenge
        </button>

        <button
          type="button"
          className={`primary-button submit-ready-btn ${isTimeUp ? "highlight-pulse" : ""}`}
          onClick={onProceedToProof}
        >
          <span>✍️</span> {isTimeUp ? "Submit Evidence & Reflection" : "I Finished Activity / Submit Proof"}
        </button>
      </div>

      {/* Abandon Confirmation Modal */}
      {confirmAbandon && (
        <div className="modal-overlay">
          <div className="modal-dialog">
            <h3>Abandon this challenge?</h3>
            <p>
              Your timer will stop and this activity won't be counted toward your streak.
              Are you sure you want to cancel?
            </p>
            <div className="modal-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setConfirmAbandon(false)}
              >
                Keep Going
              </button>
              <button
                type="button"
                className="danger-button"
                onClick={() => {
                  setConfirmAbandon(false);
                  onAbandon(challenge.id);
                }}
              >
                Yes, Abandon
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
