
function renderChat() {
  const container = document.getElementById("home-chat");
  if (!container) {
    console.error("Chat container not found.");
    return;
  }
  container.innerHTML = `
    <div id="chat-overlay" class="chat-overlay"></div>
    <div class="chat-container">

      <!-- CHAT HEADER -->
      <div class="chat-header">
        <div class="status-badge">
          <span class="dot-online"></span>
          Trợ Lý AI Đang Hoạt Động
        </div>

        <div class="chat-header-actions">
          <input
            id="chat-size-slider"
            class="chat-size-slider"
            type="range"
            min="0"
            max="100"
            step="1"
            value="45"
          />
          <button id="chat-toggle-button" class="chat-toggle-btn" type="button">
            <i class="fa-solid fa-up-right-and-down-left-from-center"></i>
          </button>
        </div>
      </div>

      <!-- CHAT BODY -->
      <i class="fa-solid fa-leaf chat-bg-logo"></i>
      <div id="chat-messages" class="chat-body"></div>

      <!-- CHAT INPUT -->
      <div id="chat-input"></div>
      </div>
    </div>
  `;
  bindChatShellEvents();
  restoreChatShellState();
}

function bindChatShellEvents() {
  const chatContainer = document.querySelector(".chat-container");
  const overlay = document.getElementById("chat-overlay");
  const toggleButton = document.getElementById("chat-toggle-button");
  const slider = document.getElementById("chat-size-slider");

  if (!chatContainer || !overlay || !toggleButton || !slider) {
    return;
  }
  toggleButton.addEventListener("click", () => {
    setChatFullscreen(!chatContainer.classList.contains("is-fullscreen"));
  });
  overlay.addEventListener("click", () => {
    setChatFullscreen(false);
  });
  slider.addEventListener("input", () => {
    const value = Number(slider.value);
    applyChatCollapsedSize(value);
    localStorage.setItem("chatCollapsedSize", String(value));
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setChatFullscreen(false);
    }
  });
}

function restoreChatShellState() {
  const savedSize = localStorage.getItem("chatCollapsedSize");
  const slider = document.getElementById("chat-size-slider");
  if (slider && savedSize != null && savedSize !== "") {
    slider.value = savedSize;
  }
  const sizeValue = slider ? Number(slider.value) : 45;
  applyChatCollapsedSize(sizeValue);
  const savedFullscreen = localStorage.getItem("chatFullscreen");
  setChatFullscreen(savedFullscreen === "1");
}

function setChatFullscreen(isFullscreen) {
  const chatContainer = document.querySelector(".chat-container");
  const overlay = document.getElementById("chat-overlay");
  const slider = document.getElementById("chat-size-slider");
  if (!chatContainer || !overlay) {
    return;
  }

  chatContainer.classList.toggle("is-fullscreen", Boolean(isFullscreen));
  overlay.classList.toggle("is-visible", Boolean(isFullscreen));
  if (slider) {
    slider.disabled = Boolean(isFullscreen);
  }
  localStorage.setItem("chatFullscreen", isFullscreen ? "1" : "0");

  const messages = document.getElementById("chat-messages");
  if (messages) {
    messages.scrollTop = messages.scrollHeight;
  }
}

function applyChatCollapsedSize(value) {
  const clamped = Math.max(0, Math.min(100, value));
  const width = Math.round(320 + clamped * 2.2);
  const height = Math.round(360 + clamped * 2.8);
  document.documentElement.style.setProperty("--chat-collapsed-width", `${width}px`);
  document.documentElement.style.setProperty("--chat-collapsed-height", `${height}px`);
}
