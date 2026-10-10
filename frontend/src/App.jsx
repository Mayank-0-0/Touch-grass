import React, { useState, useEffect, useCallback } from "react";
import Navbar from "./components/Navbar";
import Dashboard from "./components/Dashboard";
import InterestsPicker from "./components/InterestsPicker";
import ChallengeDetails from "./components/ChallengeDetails";
import ChallengeMode from "./components/ChallengeMode";
import ProofSubmission from "./components/ProofSubmission";
import ResultsView from "./components/ResultsView";
import HistoryView from "./components/HistoryView";
import { api } from "./api";
import "./App.css";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard"); // dashboard, interests, details, challenge_mode, proof, results, history
  const [stats, setStats] = useState({ current_streak: 0, longest_streak: 0, total_completed: 0 });
  const [preferences, setPreferences] = useState(null);
  const [activeChallenge, setActiveChallenge] = useState(null);
  const [stagedChallenge, setStagedChallenge] = useState(null);
  const [history, setHistory] = useState([]);
  const [aiStatus, setAiStatus] = useState(null);
  const [evaluationResult, setEvaluationResult] = useState(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [initLoaded, setInitLoaded] = useState(false);

  // Load initial app data
  const loadAppData = useCallback(async () => {
    try {
      const [statsRes, prefsRes, activeRes, historyRes, aiRes] = await Promise.allSettled([
        api.getStats(),
        api.getPreferences(),
        api.getActiveChallenge(),
        api.getHistory(),
        api.getAIStatus(),
      ]);

      if (statsRes.status === "fulfilled") setStats(statsRes.value);
      if (prefsRes.status === "fulfilled") setPreferences(prefsRes.value);
      if (historyRes.status === "fulfilled") setHistory(historyRes.value);
      if (aiRes.status === "fulfilled") setAiStatus(aiRes.value);

      if (activeRes.status === "fulfilled" && activeRes.value) {
        setActiveChallenge(activeRes.value);
        // If there's an active running challenge on refresh, resume directly into Challenge Mode!
        setActiveTab("challenge_mode");
      }
    } catch (err) {
      console.error("Failed to load initial data", err);
    } finally {
      setInitLoaded(true);
    }
  }, []);

  useEffect(() => {
    loadAppData();
  }, [loadAppData]);

  // Periodic AI status check
  const refreshAIStatus = async () => {
    try {
      const res = await api.getAIStatus();
      setAiStatus(res);
    } catch (err) {
      setAiStatus({ online: false, server_url: "http://127.0.0.1:8081", message: "AI Server unreachable" });
    }
  };

  // Generate Challenge
  const handleGenerateChallenge = async (params) => {
    setIsLoading(true);
    setError("");
    try {
      const challenge = await api.generateChallenge(params);
      setStagedChallenge(challenge);
      setActiveTab("details");
    } catch (err) {
      setError(err.message || "Failed to generate challenge. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // Start Challenge
  const handleStartChallenge = async (challengeId) => {
    setIsLoading(true);
    setError("");
    try {
      const started = await api.startChallenge(challengeId);
      setActiveChallenge(started);
      setActiveTab("challenge_mode");
    } catch (err) {
      setError(err.message || "Could not start challenge.");
    } finally {
      setIsLoading(false);
    }
  };

  // Proceed from Timer to Proof Submission
  const handleProceedToProof = () => {
    setError("");
    setActiveTab("proof");
  };

  // Submit Proof for AI Evaluation
  const handleSubmitProof = async (payload) => {
    if (!activeChallenge) return;
    setIsLoading(true);
    setError("");
    try {
      const evalRes = await api.submitProof(activeChallenge.id, payload);
      setEvaluationResult(evalRes);
      setActiveChallenge(null);

      // Refresh stats & history
      const [newStats, newHistory] = await Promise.all([api.getStats(), api.getHistory()]);
      setStats(newStats);
      setHistory(newHistory);

      setActiveTab("results");
    } catch (err) {
      // If AI server unavailable (503) or other error:
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Abandon Challenge
  const handleAbandonChallenge = async (challengeId) => {
    try {
      await api.abandonChallenge(challengeId);
    } catch (e) {
      console.warn("Abandon error", e);
    }
    setActiveChallenge(null);
    setActiveTab("dashboard");
  };

  // Surprise Me Quick Action
  const handleSurpriseMe = () => {
    handleGenerateChallenge({
      interest: null,
      duration_minutes: preferences?.default_duration || 30,
      difficulty: preferences?.default_difficulty || "Medium",
      surprise_me: true,
    });
  };

  if (!initLoaded) {
    return (
      <div className="loading-screen">
        <span className="toast-spinner" aria-hidden="true" />
        <p>Connecting to Touch Grass…</p>
      </div>
    );
  }

  return (
    <main className="app-shell">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        aiStatus={aiStatus}
        onRefreshAI={refreshAIStatus}
      />

      <section className="page-heading">
        <h1>Your life, offline.</h1>
        <p>Trade screen time for real-world adventures, skills, and mindful experiences.</p>
      </section>

      {/* Main Tabs Navigation */}
      <nav className="tabs" aria-label="Main Navigation">
        <button
          className={`tab-button ${activeTab === "dashboard" ? "active" : ""}`}
          onClick={() => setActiveTab("dashboard")}
        >
          <span className="tab-icon" aria-hidden="true">🌱</span> Dashboard
        </button>

        <button
          className={`tab-button ${activeTab === "interests" ? "active" : ""}`}
          onClick={() => {
            setError("");
            setActiveTab("interests");
          }}
        >
          <span className="tab-icon" aria-hidden="true">🎯</span> New Challenge
        </button>

        {activeChallenge && (
          <button
            className={`tab-button ${activeTab === "challenge_mode" || activeTab === "proof" ? "active highlight-tab" : "highlight-tab"}`}
            onClick={() => setActiveTab("challenge_mode")}
          >
            <span className="tab-icon" aria-hidden="true">⏱</span> Focus Timer
          </button>
        )}

        <button
          className={`tab-button ${activeTab === "history" ? "active" : ""}`}
          onClick={() => setActiveTab("history")}
        >
          <span className="tab-icon" aria-hidden="true">📖</span> History
        </button>
      </nav>

      {/* Content Container */}
      <section className="content-panel">
        {activeTab === "dashboard" && (
          <Dashboard
            stats={stats}
            activeChallenge={activeChallenge}
            history={history}
            onStartNew={() => setActiveTab("interests")}
            onSurpriseMe={handleSurpriseMe}
            onResumeChallenge={() => setActiveTab("challenge_mode")}
            onViewHistory={() => setActiveTab("history")}
          />
        )}

        {activeTab === "interests" && (
          <InterestsPicker
            preferences={preferences}
            onGenerate={handleGenerateChallenge}
            isLoading={isLoading}
            error={error}
          />
        )}

        {activeTab === "details" && stagedChallenge && (
          <ChallengeDetails
            challenge={stagedChallenge}
            onStart={handleStartChallenge}
            onRegenerate={() => setActiveTab("interests")}
            isLoading={isLoading}
          />
        )}

        {activeTab === "challenge_mode" && activeChallenge && (
          <ChallengeMode
            challenge={activeChallenge}
            onProceedToProof={handleProceedToProof}
            onAbandon={handleAbandonChallenge}
          />
        )}

        {activeTab === "proof" && activeChallenge && (
          <ProofSubmission
            challenge={activeChallenge}
            onSubmit={handleSubmitProof}
            isLoading={isLoading}
            error={error}
            onBackToTimer={() => setActiveTab("challenge_mode")}
          />
        )}

        {activeTab === "results" && (
          <ResultsView
            challenge={activeChallenge}
            evaluationResult={evaluationResult}
            onStartAnother={() => setActiveTab("interests")}
            onGoToDashboard={() => setActiveTab("dashboard")}
            onGoToHistory={() => setActiveTab("history")}
          />
        )}

        {activeTab === "history" && (
          <HistoryView
            history={history}
            onStartNew={() => setActiveTab("interests")}
          />
        )}
      </section>
    </main>
  );
}
