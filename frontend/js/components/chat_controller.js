
let chatHistory = [];

async function handleChatImageSelected(file) {
  if (!file || !(file instanceof File)) {
    return;
  }
  const maxBytes = 7 * 1024 * 1024;
  if (file.size > maxBytes) {
    chatHistory.push({
      role: "assistant",
      content: "Ảnh quá lớn. Bạn vui lòng chọn ảnh nhỏ hơn (dưới 7MB).",
    });
    renderChatMessages(chatHistory);
    return;
  }

  const dataUrl = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
  chatHistory.push({
    role: "user",
    content: "",
    attachments: [
      {
        type: "image",
        name: file.name,
        dataUrl: String(dataUrl || ""),
      },
    ],
  });
  renderChatMessages(chatHistory);

  const input = document.getElementById("chat-input-field");
  if (input) {
    input.focus();
  }
}

async function handleChatSend() {
  const input = document.getElementById("chat-input-field");
  const sendButton = document.getElementById("chat-send-button");
  if (!input || !sendButton) {
    console.error("Chat input elements not found.");
    return;
  }
  const text = input.value.trim();
  console.log("[FRONTEND] handleChatSend TEXT:", JSON.stringify(text));
  if (!text) {
    return;
  }
  chatHistory.push({
    role: "user",
    content: text,
  });
  renderChatMessages(chatHistory);

  input.value = "";
  input.disabled = true;
  sendButton.disabled = true;
  try {
    const conversationHistory = chatHistory.slice(0, -1);
    console.log("[FRONTEND] conversationHistory:", JSON.stringify(conversationHistory));

    // Add empty assistant message that will be updated progressively
    chatHistory.push({
      role: "assistant",
      content: "",
    });
    renderChatMessages(chatHistory);
    const lastMessageIndex = chatHistory.length - 1;
    await chatMessageStream(text, conversationHistory, (chunk) => {
      chatHistory[lastMessageIndex].content += chunk;
      renderChatMessages(chatHistory);
    });

    if (typeof refreshRoadmapData === "function") {
      await refreshRoadmapData();
    }
  } catch (error) {
    console.error("Chat API error:", error);
    let errorMessage = "Không thể kết nối với hệ thống AI. Vui lòng thử lại.";
    if (error.name === "AbortError") {
      errorMessage = "Hệ thống AI phản hồi quá lâu. Vui lòng thử lại sau.";
    }
    const lastMessageIndex = chatHistory.length - 1;
    if (chatHistory[lastMessageIndex].role === "assistant" && chatHistory[lastMessageIndex].content === "") {
      chatHistory[lastMessageIndex].content = errorMessage;
    } else {
      chatHistory.push({
        role: "assistant",
        content: errorMessage,
      });
    }
    renderChatMessages(chatHistory);
  } finally {
    input.disabled = false;
    sendButton.disabled = false;
    input.focus();
  }
}

function buildAssistantMessage(result) {
  if (!result) {
    return "Mình chưa nhận được kết quả từ hệ thống AI.";
  }
  if (result.needs_clarification) {
    return (
      result.clarification_question ||
      "Mình cần thêm một chút thông tin để xử lý yêu cầu này."
    );
  }

  if (result.status === "accepted") {
    if (result.intent === "add_expense") {
      const amount = result.entities?.amount;
      if (amount != null) {
        return `Mình đã ghi nhận khoản chi ${formatCurrency(amount)}.`;
      }
      return "Mình đã ghi nhận khoản chi của bạn.";
    }
    return `Mình đã xử lý yêu cầu "${result.intent}".`;
  }
  return "Mình đã nhận yêu cầu nhưng cần thêm thông tin để xử lý.";
}

function formatCurrency(amount) {
  if (typeof amount !== "number") {
    return String(amount);
  }
  return new Intl.NumberFormat("vi-VN").format(amount) + " VNĐ";
}
