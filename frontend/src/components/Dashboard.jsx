import React from "react";

export default function Dashboard({
  stats,
  activeChallenge,
  history,
  onStartNew,
  onSurpriseMe,
  onResumeChallenge,
  onViewHistory,
}) {
  const recentItems = (history || []).slice(0, 3);

  return (
    <div className="dashboard-view">
      {/* Welcome Heading */}
      <div className="section-heading">
        <h2>Welcome to Touch Grass</h2>
        <p>Step away from the screen, recharge your senses, and embrace the offline world.</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-icon" aria-hidden="true">🔥</span>
          <div className="stat-info">
            <span className="stat-value">{stats?.current_streak || 0}</span>
            <span className="stat-label">Day Streak</span>
          </div>
        </div>

        <div className="stat-card">
          <span className="stat-icon" aria-hidden="true">🏆</span>
          <div className="stat-info">
            <span className="stat-value">{stats?.longest_streak || 0}</span>
            <span className="stat-label">Best Streak</span>
          </div>
        </div>

        <div className="stat-card">
          <span className="stat-icon" aria-hidden="true">🌿</span>
          <div className="stat-info">
            <span className="stat-value">{stats?.total_completed || 0}</span>
            <span className="stat-label">Completed Activities</span>
          </div>
        </div>
      </div>

      {/* Active Challenge Notice */}
      {activeChallenge && activeChallenge.status === "active" && (
        <div className="active-challenge-banner">
          <div className="banner-content">
            <div className="banner-badge">In Progress</div>
            <h3>{activeChallenge.title}</h3>
            <p>
              Category: <strong>{activeChallenge.interest}</strong> • Target Duration:{" "}
              <strong>{activeChallenge.duration_minutes} minutes</strong>
            </p>
          </div>
          <button className="primary-button" onClick={onResumeChallenge}>
            <span>⏱</span> Resume Challenge Mode
          </button>
        </div>
      )}

      {/* Action Prompts */}
      <div className="action-cards-grid">
        <div className="action-card">
          <div className="action-card-header">
            <span className="action-card-icon">🎯</span>
            <h3>Choose Your Activity</h3>
          </div>
          <p>Select your favorite offline interests, choose a duration (30 min to 2 hours), and let AI create an activity.</p>
          <button className="primary-button" onClick={onStartNew}>
            <span>✦</span> Start Custom Challenge
          </button>
        </div>

        <div className="action-card surprise-card">
          <div className="action-card-header">
            <span className="action-card-icon">🎲</span>
            <h3>Surprise Me!</h3>
          </div>
          <p>No decision fatigue. Let the AI instantly pick a delightful, screenless activity for you to try right now.</p>
          <button className="secondary-button" onClick={onSurpriseMe}>
            <span>✨</span> Surprise Me Now
          </button>
        </div>
      </div>

      {/* Recent History */}
      <div className="recent-section">
        <div className="recent-header">
          <h3>Recent Offline Achievements</h3>
          {history && history.length > 0 && (
            <button className="text-button" onClick={onViewHistory}>
              View All History →
            </button>
          )}
        </div>

        {recentItems.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon" aria-hidden="true">🌱</span>
            <strong>No activities completed yet</strong>
            <p>Start your first screenless challenge today to begin your streak!</p>
          </div>
        ) : (
          <div className="recent-list">
            {recentItems.map((item) => (
              <div className="recent-item-card" key={item.id}>
                <div className="recent-item-main">
                  <div className="recent-title-row">
                    <span className="recent-interest-badge">{item.interest}</span>
                    <h4>{item.title}</h4>
                  </div>
                  {item.feedback && (
                    <p className="recent-feedback">"{item.feedback}"</p>
                  )}
                  <span className="recent-date">
                    Completed: {item.submitted_at ? new Date(item.submitted_at).toLocaleDateString() : "Recently"}
                  </span>
                </div>
                <div className="recent-score-badge">
                  <span className="score-num">{item.score}</span>
                  <span className="score-den">/100</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
