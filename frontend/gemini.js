// ─── Nexus Social — gemini.js (Frontend API Client) ───────────────────────────
// Pure HTTP client. Zero AI logic. All business logic lives in Python backend.

const API = '';

async function apiFetch(endpoint, body) {
  const res = await fetch(`${API}/api/${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err?.detail || `API error ${res.status}`);
  }
  return res.json();
}

async function geminiGenerateCaptions(description, style, platform) {
  const data = await apiFetch('social/captions', { description, style, platform });
  return data.captions; // returns array of 3 strings
}

async function geminiGenerateHashtags(topic) {
  const data = await apiFetch('social/hashtags', { topic });
  return data.hashtags.join('\n'); // returns newline-separated string for compatibility
}

async function geminiModerateContent(content) {
  const data = await apiFetch('social/moderate', { content });
  return data; // returns full moderation object
}

async function geminiAnalyseSentiment(text) {
  const data = await apiFetch('social/sentiment', { text });
  return data.analysis;
}

async function geminiGrowthAdvice(niche) {
  const data = await apiFetch('social/growth', { niche });
  return data.strategy;
}

async function geminiPredictPerformance(post) {
  const data = await apiFetch('social/predict', { post });
  return data.prediction;
}

async function geminiSmartSearch(query) {
  const data = await apiFetch('social/search', { query });
  return data.results; // returns array
}

async function geminiTrendingSummary(hashtag) {
  const data = await apiFetch('social/trending-summary', { hashtag });
  return data.summary;
}
