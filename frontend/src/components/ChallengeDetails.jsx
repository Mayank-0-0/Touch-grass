import React from "react";

export default function ChallengeDetails({
  challenge,
  onStart,
  onRegenerate,
  isLoading,
}) {
  if (!challenge) return null;

  return (
    <div className="details-view">
      <div className="details-header-card">
        <div className="details-badge-row">
          <span className="meta-chip interest-chip-static">🌿 {challenge.interest}</span>
          <span className="meta-chip duration-chip-static">⏱ {challenge.duration_minutes} Minutes</span>
          <span className="meta-chip difficulty-chip-static">⚡ {challenge.difficulty}</span>
          {challenge.is_fallback && (
            <span className="meta-chip fallback-chip-static" title="Generated from curated offline library while local AI server is offline">
              📦 Curated Challenge
            </span>
          )}
        </div>
        <h2 className="challenge-hero-title">{challenge.title}</h2>
      </div>

      {/* Screenless Commitment Banner */}
      <div className="offline-notice-box">
        <span className="notice-icon" aria-hidden="true">📵</span>
        <div className="notice-copy">
          <strong>Screen-Free Commitment</strong>
          <p>
            This challenge requires zero digital screens. Once you click "Start Challenge",
            place your computer or phone aside and immerse yourself in the physical activity.
          </p>
        </div>
      </div>

      {/* Instructions */}
      <div className="details-section">
        <h3>Step-by-Step Instructions</h3>
        <p className="instructions-body">{challenge.instructions}</p>
      </div>

      {/* Materials */}
      {challenge.materials && challenge.materials.length > 0 && (
        <div className="details-section">
          <h3>Required Materials</h3>
          <ul className="materials-list">
            {(Array.isArray(challenge.materials)
              ? challenge.materials
              : [challenge.materials]
            ).map((mat, i) => (
              <li key={i}>
                <span className="material-bullet">▪</span> {mat}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Expected Result */}
      {challenge.expected_result && (
        <div className="details-section">
          <h3>Expected Real-World Outcome</h3>
          <p className="expected-outcome-text">{challenge.expected_result}</p>
        </div>
      )}

      {/* Proof Instructions Preview */}
      {challenge.proof_instructions && (
        <div className="details-section proof-preview-section">
          <h3>Verification & Reflection Instructions</h3>
          <p>{challenge.proof_instructions}</p>
          <div className="proof-tip">
            💡 When you return, the AI will ask you 2-3 specific questions about what you observed or accomplished.
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="details-actions">
        <button
          type="button"
          className="secondary-button"
          onClick={onRegenerate}
          disabled={isLoading}
        >
          <span>↻</span> Pick Another Activity
        </button>

        <button
          type="button"
          className="primary-button cta-start-btn"
          onClick={() => onStart(challenge.id)}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="button-spinner" /> Starting…
            </>
          ) : (
            <>
              <span>🚀</span> Start Challenge & Begin Timer
            </>
          )}
        </button>
      </div>
    </div>
  );
}
