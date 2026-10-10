import React, { useState } from "react";

const AVAILABLE_INTERESTS = [
  { id: "Walking", label: "Walking", icon: "🚶" },
  { id: "Reading", label: "Reading", icon: "📖" },
  { id: "Gardening", label: "Gardening", icon: "🌱" },
  { id: "Drawing", label: "Drawing & Sketching", icon: "✏️" },
  { id: "Cooking", label: "Cooking & Baking", icon: "🍳" },
  { id: "Hiking", label: "Hiking & Outdoors", icon: "🌲" },
  { id: "Sports", label: "Sports & Mobility", icon: "🏃" },
  { id: "Music", label: "Music & Acoustic Listening", icon: "🎵" },
  { id: "Writing", label: "Handwriting & Journaling", icon: "✍️" },
];

const DURATION_OPTIONS = [
  { value: 30, label: "30 Minutes", desc: "A brief, mindful break" },
  { value: 60, label: "1 Hour", desc: "Solid focused immersion" },
  { value: 120, label: "2 Hours", desc: "Deep offline exploration" },
];

const DIFFICULTY_OPTIONS = ["Easy", "Medium", "Hard"];

export default function InterestsPicker({
  preferences,
  onGenerate,
  isLoading,
  error,
}) {
  const [selectedInterests, setSelectedInterests] = useState(
    preferences?.selected_interests?.length ? preferences.selected_interests : ["Walking", "Reading"]
  );
  const [duration, setDuration] = useState(preferences?.default_duration || 30);
  const [difficulty, setDifficulty] = useState(preferences?.default_difficulty || "Medium");

  function toggleInterest(interestId) {
    if (selectedInterests.includes(interestId)) {
      if (selectedInterests.length > 1) {
        setSelectedInterests(selectedInterests.filter((id) => id !== interestId));
      }
    } else {
      setSelectedInterests([...selectedInterests, interestId]);
    }
  }

  function handleGenerate() {
    // Pick randomly among selected interests to provide variety
    const chosenInterest =
      selectedInterests[Math.floor(Math.random() * selectedInterests.length)];

    onGenerate({
      interest: chosenInterest,
      duration_minutes: duration,
      difficulty: difficulty,
      surprise_me: false,
    });
  }

  function handleSurpriseMe() {
    onGenerate({
      interest: null,
      duration_minutes: duration,
      difficulty: difficulty,
      surprise_me: true,
    });
  }

  return (
    <div className="picker-view">
      <div className="section-heading">
        <h2>Choose Your Offline Interests</h2>
        <p>Tailor your activity so it fits your schedule, environment, and preferred ways to unplug.</p>
      </div>

      {error && (
        <div className="error-banner" role="alert">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* 1. Interests Grid */}
      <div className="picker-section">
        <label className="picker-label">
          1. Select one or more interests
          <span className="picker-sublabel">The AI will vary tasks based on your selections</span>
        </label>
        <div className="interests-grid">
          {AVAILABLE_INTERESTS.map((item) => {
            const isSelected = selectedInterests.includes(item.id);
            return (
              <button
                type="button"
                key={item.id}
                className={`interest-chip ${isSelected ? "selected" : ""}`}
                onClick={() => toggleInterest(item.id)}
              >
                <span className="chip-icon">{item.icon}</span>
                <span className="chip-label">{item.label}</span>
                {isSelected && <span className="chip-check">✓</span>}
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Duration Selection */}
      <div className="picker-section">
        <label className="picker-label">
          2. Choose Challenge Duration
          <span className="picker-sublabel">Be honest about how long you can commit away from all screens</span>
        </label>
        <div className="duration-grid">
          {DURATION_OPTIONS.map((opt) => (
            <button
              type="button"
              key={opt.value}
              className={`duration-card ${duration === opt.value ? "selected" : ""}`}
              onClick={() => setDuration(opt.value)}
            >
              <div className="duration-time">{opt.label}</div>
              <div className="duration-desc">{opt.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* 3. Difficulty */}
      <div className="picker-section">
        <label className="picker-label">
          3. Choose Difficulty Level
        </label>
        <div className="difficulty-row">
          {DIFFICULTY_OPTIONS.map((diff) => (
            <button
              type="button"
              key={diff}
              className={`difficulty-btn ${difficulty === diff ? "selected" : ""}`}
              onClick={() => setDifficulty(diff)}
            >
              {diff}
            </button>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="picker-actions">
        <button
          type="button"
          className="secondary-button"
          onClick={handleSurpriseMe}
          disabled={isLoading}
        >
          <span>🎲</span> Surprise Me Instead
        </button>

        <button
          type="button"
          className="primary-button"
          onClick={handleGenerate}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="button-spinner" /> Generating Activity…
            </>
          ) : (
            <>
              <span>✦</span> Generate Challenge
            </>
          )}
        </button>
      </div>
    </div>
  );
}
