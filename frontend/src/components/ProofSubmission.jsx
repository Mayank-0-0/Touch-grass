import React, { useState } from "react";

export default function ProofSubmission({
  challenge,
  onSubmit,
  isLoading,
  error,
  onBackToTimer,
}) {
  const defaultQuestions = challenge.follow_up_questions?.length
    ? challenge.follow_up_questions
    : [
        "Describe what you created, observed, or completed in detail.",
        "What was the most engaging moment during this offline period?",
        "What physical sensations or details did you notice away from screens?",
      ];

  // Initialize answers object mapping each question to empty string
  const [answers, setAnswers] = useState(() => {
    const initial = {};
    defaultQuestions.forEach((q) => {
      // If proof_answers was already saved (e.g. from previous attempt), pre-fill it
      if (challenge.proof_answers && typeof challenge.proof_answers === "object") {
        initial[q] = challenge.proof_answers[q] || "";
      } else {
        initial[q] = "";
      }
    });
    return initial;
  });

  const [imagePreview, setImagePreview] = useState(challenge.proof_image || null);
  const [validationError, setValidationError] = useState("");

  function handleAnswerChange(question, text) {
    setAnswers((prev) => ({
      ...prev,
      [question]: text,
    }));
    setValidationError("");
  }

  function handleImageUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setValidationError("Please select a valid image file (PNG, JPG, WebP).");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setValidationError("Image file must be under 5MB.");
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      setImagePreview(event.target?.result);
    };
    reader.readAsDataURL(file);
  }

  function handleRemoveImage() {
    setImagePreview(null);
  }

  function handleSubmit(e) {
    e.preventDefault();

    // Validate that at least one question has been answered with substance
    const totalAnswerLength = Object.values(answers).reduce(
      (acc, curr) => acc + (curr ? curr.trim().length : 0),
      0
    );

    if (totalAnswerLength < 15) {
      setValidationError(
        "Please provide a few sentences describing your offline activity and reflections before submitting."
      );
      return;
    }

    onSubmit({
      proof_answers: answers,
      proof_image: imagePreview,
    });
  }

  return (
    <div className="proof-view">
      <div className="section-heading">
        <h2>Submit Activity Proof & Reflection</h2>
        <p>
          Reflect on your offline experience. Local Gemma will evaluate your observations
          and award your score and streak.
        </p>
      </div>

      {/* Challenge Summary Bar */}
      <div className="proof-challenge-summary">
        <div>
          <span className="summary-title">Activity: {challenge.title}</span>
          <span className="summary-meta">
            {challenge.interest} • {challenge.duration_minutes} minutes • {challenge.difficulty}
          </span>
        </div>
        {onBackToTimer && (
          <button type="button" className="text-button" onClick={onBackToTimer}>
            ← Back to Timer
          </button>
        )}
      </div>

      {/* Backend / AI Error Banner */}
      {error && (
        <div className="error-banner proof-error-banner" role="alert">
          <span className="error-icon">⚠️</span>
          <div className="error-body">
            <strong>Evaluation Notice</strong>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Validation Error Banner */}
      {validationError && (
        <div className="warning-banner" role="alert">
          <span className="warning-icon">ℹ️</span>
          <span>{validationError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="proof-form">
        {/* Dynamic Follow-up Questions */}
        <div className="questions-section">
          <div className="questions-header">
            <h3>Reflection Questions</h3>
            <span className="questions-caption">Answer thoughtfully based on what you physically experienced</span>
          </div>

          {defaultQuestions.map((question, index) => (
            <div className="question-field" key={index}>
              <label htmlFor={`question-${index}`} className="question-label">
                <span className="question-number">{index + 1}.</span> {question}
              </label>
              <textarea
                id={`question-${index}`}
                className="proof-textarea"
                rows="3"
                placeholder="Share your specific real-world observations..."
                value={answers[question] || ""}
                onChange={(e) => handleAnswerChange(question, e.target.value)}
                disabled={isLoading}
              />
            </div>
          ))}
        </div>

        {/* Optional Image Upload */}
        <div className="image-upload-section">
          <label className="picker-label">
            Optional Photo or Sketch
            <span className="picker-sublabel">
              Upload a snapshot of your creation, plant, dish, sketch, or route landmark (optional)
            </span>
          </label>

          {imagePreview ? (
            <div className="image-preview-card">
              <img src={imagePreview} alt="Uploaded proof preview" className="proof-thumbnail" />
              <div className="preview-controls">
                <span className="preview-status">✓ Photo attached</span>
                <button
                  type="button"
                  className="remove-img-btn"
                  onClick={handleRemoveImage}
                  disabled={isLoading}
                >
                  Remove Photo
                </button>
              </div>
            </div>
          ) : (
            <label className="upload-dropzone">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                disabled={isLoading}
                className="file-input-hidden"
              />
              <span className="upload-icon">📷</span>
              <span className="upload-cta">Click to upload an optional photo</span>
              <span className="upload-specs">PNG, JPG, or WebP up to 5MB</span>
            </label>
          )}
        </div>

        {/* Submit Actions */}
        <div className="proof-actions">
          <button
            type="submit"
            className="primary-button submit-evaluation-btn"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="button-spinner" /> Evaluating with Local AI…
              </>
            ) : (
              <>
                <span>✦</span> Submit for AI Evaluation
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
