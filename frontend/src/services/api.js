const API_BASE_URL = "http://127.0.0.1:8002";

export async function getHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error("The InvestTwin API is unavailable.");
  }

  return response.json();
}

async function requestProfile(path, method, profile) {
  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (profile !== undefined && profile !== null) {
    options.body = JSON.stringify(profile);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, options);

  const body = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      body.detail || body.error?.message || "Unable to complete the profile request."
    );
  }

  return body;
}

// Profile
export function saveProfile(profile) {
  return requestProfile("/api/v1/profile", "POST", profile);
}

export function getProfile(userId) {
  return requestProfile(
    `/api/v1/profile/${encodeURIComponent(userId)}`,
    "GET"
  );
}

// Data sources
export function getDataSources() {
  return requestProfile("/api/v1/data-sources/status", "GET");
}

// Market
export function getStock(symbol) {
  return requestProfile(
    `/api/v1/market/stocks/${encodeURIComponent(symbol)}`,
    "GET"
  );
}

export function getMutualFunds(query) {
  return requestProfile(
    `/api/v1/market/mutual-funds?query=${encodeURIComponent(query)}`,
    "GET"
  );
}

// Analysis
export function getStockAnalysis(symbol) {
  return requestProfile(
    `/api/v1/analysis/stocks/${encodeURIComponent(symbol)}`,
    "GET"
  );
}

export function getStockAnalysisHistory(symbol) {
  return requestProfile(
    `/api/v1/analysis/stocks/${encodeURIComponent(symbol)}/history`,
    "GET"
  );
}

// Portfolio
export function getPortfolioRecommendation(payload) {
  return requestProfile(
    "/api/v1/portfolio/recommend",
    "POST",
    payload
  );
}

// Investment history
export function getHistory(userId) {
  return requestProfile(
    `/api/v1/history?user_id=${encodeURIComponent(userId)}`,
    "GET"
  );
}

export function analyzeHistory(userId) {
  return requestProfile(
    `/api/v1/history/analysis?user_id=${encodeURIComponent(userId)}`,
    "GET"
  );
}

export function createTransaction(transaction) {
  return requestProfile(
    "/api/v1/history",
    "POST",
    transaction
  );
}

export async function importHistory(userId, file) {
  const formData = new FormData();

  formData.append("user_id", userId);
  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/api/v1/history/import`,
    {
      method: "POST",
      body: formData,
    }
  );

  const body = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      body.detail || "Unable to import investment history."
    );
  }

  return body;
}

// Stress testing
export function runStress(payload) {
  return requestProfile(
    "/api/v1/stress-tests/run",
    "POST",
    payload
  );
}

export function saveStress(payload) {
  return requestProfile(
    "/api/v1/stress-tests",
    "POST",
    payload
  );
}

export function getStressHistory(userId) {
  return requestProfile(
    `/api/v1/stress-tests?user_id=${encodeURIComponent(userId)}`,
    "GET"
  );
}

// AI
export function getAIStatus() {
  return requestProfile("/api/v1/ai/status", "GET");
}

export function getAIContext(userId) {
  return requestProfile(
    `/api/v1/ai/context?user_id=${encodeURIComponent(userId)}`,
    "GET"
  );
}

export function explainPortfolio(payload) {
  return requestProfile(
    "/api/v1/ai/explain/portfolio",
    "POST",
    payload
  );
}

export function askAITwin(question, context) {
  return requestProfile(
    "/api/v1/ai/chat",
    "POST",
    {
      question,
      context,
    }
  );
}

// Monitoring
export function runMonitoring(payload) {
  return requestProfile(
    "/api/v1/monitoring/check",
    "POST",
    payload
  );
}

export function reevaluateTwin(payload) {
  return requestProfile(
    "/api/v1/monitoring/reevaluate",
    "POST",
    payload
  );
}

export function resetDemo() {
  return requestProfile(
    "/api/v1/demo/reset",
    "POST",
    {}
  );
}

export function getMonitoringSnapshots(userId) {
  return requestProfile(
    `/api/v1/monitoring/snapshot/history?user_id=${encodeURIComponent(
      userId
    )}`,
    "GET"
  );
}

export function getMonitoringEvents(userId) {
  return requestProfile(
    `/api/v1/monitoring/events?user_id=${encodeURIComponent(userId)}`,
    "GET"
  );
}

export function getMonitoringChanges(userId) {
  return requestProfile(
    `/api/v1/monitoring/changes?user_id=${encodeURIComponent(userId)}`,
    "GET"
  );
}

export function updateMonitoringEvent(eventId, action) {
  return requestProfile(
    `/api/v1/monitoring/events/${encodeURIComponent(
      eventId
    )}/${action}`,
    "POST"
  );
}