
function renderChatInput() {
  const container = document.getElementById("chat-input");
  if (!container) {
    console.error("Chat input container not found.");
    return;
  }
  container.innerHTML = `
    <div class="input-area">
      <div class="input-box">
        <button
          id="chat-camera-button"
          class="action-btn"
          type="button"
        >
          <i class="fa-solid fa-camera"></i>
        </button>
        <input
          id="chat-image-input"
          type="file"
          accept="image/*"
          style="display:none"
        />
        <button
          id="chat-voice-button"
          class="action-btn"
          type="button"
        >
          <i class="fa-solid fa-microphone"></i>
        </button>

        <input
          id="chat-input-field"
          type="text"
          placeholder="Nhập câu hỏi hoặc tải hóa đơn lên..."
        />

        <button
          id="chat-send-button"
          class="btn-submit"
          type="button"
        >
          <i class="fa-solid fa-arrow-up"></i>
        </button>
      </div>
    </div>
  `;
}

function bindChatInputEvents() {
  const input = document.getElementById("chat-input-field");
  const sendButton = document.getElementById("chat-send-button");
  const cameraButton = document.getElementById("chat-camera-button");
  const imageInput = document.getElementById("chat-image-input");

  if (!input || !sendButton) {
    console.error("Chat input elements not found.");
    return;
  }
  sendButton.addEventListener("click", handleChatSend);
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleChatSend();
    }
  });

  if (cameraButton && imageInput) {
    cameraButton.addEventListener("click", () => {
      imageInput.click();
    });
    imageInput.addEventListener("change", () => {
      const file = imageInput.files?.[0];
      if (!file) {
        return;
      }
      if (typeof handleChatImageSelected === "function") {
        handleChatImageSelected(file);
      }
      imageInput.value = "";
    });
  }
}
