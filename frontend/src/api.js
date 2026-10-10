const API_BASE = "http://127.0.0.1:8000";

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data?.detail || data?.message || `Request failed with status ${response.status}`;
      const err = new Error(errorMsg);
      err.status = response.status;
      err.data = data;
      throw err;
    }

    return data;
  } catch (error) {
    if (error.status) throw error;
    // Network error (server down)
    const netErr = new Error(`Cannot connect to Touch Grass backend at ${API_BASE}. Make sure the backend server is running.`);
    netErr.status = 0;
    throw netErr;
  }
}

export const api = {
  getAIStatus: () => request("/api/ai/status"),
  getPreferences: () => request("/api/preferences"),
  updatePreferences: (data) => request("/api/preferences", { method: "PUT", body: JSON.stringify(data) }),
  getStats: () => request("/api/stats"),
  generateChallenge: (params) => request("/api/challenges/generate", { method: "POST", body: JSON.stringify(params) }),
  getActiveChallenge: () => request("/api/challenges/active"),
  getChallenge: (id) => request(`/api/challenges/${id}`),
  startChallenge: (id) => request(`/api/challenges/${id}/start`, { method: "POST" }),
  submitProof: (id, payload) => request(`/api/challenges/${id}/submit`, { method: "POST", body: JSON.stringify(payload) }),
  abandonChallenge: (id) => request(`/api/challenges/${id}/abandon`, { method: "POST" }),
  getHistory: () => request("/api/history"),
};
