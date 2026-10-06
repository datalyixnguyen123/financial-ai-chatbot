
function renderChatMessages(messages = []) {
  const container = document.getElementById("chat-messages");
  if (!container) {
    console.error("Chat messages container not found.");
    return;
  }

  container.innerHTML = "";
  messages.forEach((message) => {
    const messageElement = document.createElement("div");
    messageElement.className =
      message.role === "user"
        ? "msg-box msg-user"
        : "msg-box";
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = message.content ?? "";

    const attachments = Array.isArray(message.attachments)
      ? message.attachments
      : [];
    if (attachments.length > 0) {
      const media = document.createElement("div");
      media.className = "bubble-media";

      attachments.forEach((attachment) => {
        if (attachment?.type === "image" && attachment?.dataUrl) {
          const img = document.createElement("img");
          img.className = "chat-image";
          img.src = attachment.dataUrl;
          img.alt = attachment.name || "Ảnh đã tải lên";
          img.loading = "lazy";
          media.appendChild(img);
        }
      });

      if (media.childElementCount > 0) {
        bubble.appendChild(media);
      }
    }
    messageElement.appendChild(bubble);
    container.appendChild(messageElement);
  });

  container.scrollTop = container.scrollHeight;
}
