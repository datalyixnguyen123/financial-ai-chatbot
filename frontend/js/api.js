
const API_BASE_URL = "http://127.0.0.1:8000";

async function fetchWithTimeout(url, options = {}, timeout = 15000) {
  const controller = new AbortController();
  const timer = setTimeout(() => {
    controller.abort();
  }, timeout);

  try {
    return await fetch(url, {
      ...options,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timer);
  }
}

async function analyzeMessage(message) {
  console.log("[FRONTEND] MESSAGE:", JSON.stringify(message));
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/ai/analyze`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
      }),
    },
    15000
  );
}

async function chatMessageStream(message, conversationHistory = [], onChunk) {
  const response = await fetch(`${API_BASE_URL}/api/ai/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,
      conversation_history: conversationHistory,
      stream: true
    }),
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    
    // Process SSE format: "data: {...}\n\n"
    const lines = buffer.split("\n\n");
    buffer = lines.pop(); // Keep the last incomplete part in the buffer

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const dataStr = line.replace("data: ", "").trim();
        if (dataStr === "[DONE]") {
          return;
        }
        try {
          const data = JSON.parse(dataStr);
          if (data.response) {
            onChunk(data.response);
          }
        } catch (e) {
          console.error("Error parsing JSON chunk from stream", e);
        }
      }
    }
  }
}

async function getTransactions() {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/transactions`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    },
    15000
  );
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return await response.json();
}

async function createTransaction(payload) {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/transactions`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
    15000
  );
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API request failed: ${response.status} ${text}`);
  }
  return await response.json();
}

async function getMonthlySummary(month) {
  const url = month
    ? `${API_BASE_URL}/api/financial/monthly-summary?month=${encodeURIComponent(month)}`
    : `${API_BASE_URL}/api/financial/monthly-summary`;
  const response = await fetchWithTimeout(
    url,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    },
    15000
  );
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return await response.json();
}

async function getStudyRoadmap() {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/study-roadmap`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    },
    15000
  );
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return await response.json();
}

async function toggleStudyRoadmapAction(planId, actionId, completed) {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/study-roadmap/${encodeURIComponent(planId)}/actions/${encodeURIComponent(actionId)}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        completed: completed,
      }),
    },
    15000
  );
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API request failed: ${response.status} ${text}`);
  }
  return await response.json();
}

