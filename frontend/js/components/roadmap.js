let roadmapState = {
  rendered: false,
  data: null,
  isSubmitting: false,
};

function renderRoadmapPage() {
  const container = document.getElementById("page-roadmap");
  if (!container) {
    return;
  }

  if (!roadmapState.rendered) {
    container.innerHTML = `
      <div class="roadmap-page">
        <div id="roadmap-cards" class="roadmap-grid"></div>
        <div id="roadmap-details" class="table-card roadmap-detail-card"></div>
      </div>
    `;
    bindRoadmapEvents();
    roadmapState.rendered = true;
  }

  refreshRoadmapData();
}

function bindRoadmapEvents() {
  const detailContainer = document.getElementById("roadmap-details");
  if (!detailContainer) {
    return;
  }

  detailContainer.addEventListener("change", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLInputElement) || target.type !== "checkbox") {
      return;
    }

    const planId = String(target.dataset.planId || "");
    const actionId = String(target.dataset.actionId || "");
    if (!planId || !actionId || roadmapState.isSubmitting) {
      return;
    }

    roadmapState.isSubmitting = true;
    target.disabled = true;

    try {
      await toggleStudyRoadmapAction(planId, actionId, target.checked);
      await refreshRoadmapData();
    } catch (error) {
      console.error(error);
      target.checked = !target.checked;
    } finally {
      roadmapState.isSubmitting = false;
      target.disabled = false;
    }
  });
}

async function refreshRoadmapData() {
  try {
    const data = await getStudyRoadmap();
    roadmapState.data = data;
    renderRoadmapCards(data);
    renderRoadmapDetails(data);
  } catch (error) {
    console.error(error);
  }
}

function renderRoadmapCards(data) {
  const container = document.getElementById("roadmap-cards");
  if (!container) {
    return;
  }

  const plans = Array.isArray(data?.plans) ? data.plans.slice(0, 3) : [];
  if (!plans.length) {
    container.innerHTML = `
      <div class="roadmap-empty-card">
        <div class="roadmap-empty-title">Chưa có mục tiêu học tập</div>
        <div class="roadmap-empty-text">
          Hãy chat với AI để tạo lộ trình mới. Ví dụ: "Tôi muốn ôn IELTS 7.0 trong 60 ngày".
        </div>
      </div>
    `;
    return;
  }

  container.innerHTML = plans
    .map(
      (plan) => `
        <div class="subject-card">
          <div class="roadmap-card-top">
            <div>
              <div class="roadmap-card-title">${escapeRoadmapHtml(plan.topic)}</div>
              <div class="roadmap-card-target">${escapeRoadmapHtml(plan.target_label)}</div>
            </div>
            <span class="roadmap-badge">${escapeRoadmapHtml(plan.status_label)}</span>
          </div>

          <div class="progress-bar">
            <div class="progress-fill" style="width:${Math.max(0, Math.min(100, Number(plan.progress_percent || 0)))}%"></div>
          </div>

          <div class="roadmap-card-meta">
            <span>Tiến độ: ${Number(plan.progress_percent || 0)}%</span>
            <span>${Number(plan.completed_actions || 0)}/${Number(plan.total_actions || 0)} đầu việc</span>
          </div>
          <div class="roadmap-card-meta roadmap-card-meta-secondary">
            <span>Còn ${Number(plan.days_remaining || 0)} ngày</span>
            <span>Hạn ${escapeRoadmapHtml(formatRoadmapDate(plan.target_date))}</span>
          </div>
        </div>
      `
    )
    .join("");
}

function renderRoadmapDetails(data) {
  const container = document.getElementById("roadmap-details");
  if (!container) {
    return;
  }

  const plans = Array.isArray(data?.plans) ? data.plans : [];
  if (!plans.length) {
    container.innerHTML = `
      <div class="roadmap-empty-state">
        <div class="roadmap-empty-title">Lộ trình sẽ xuất hiện sau khi người dùng chia sẻ mục tiêu học</div>
        <div class="roadmap-empty-text">${escapeRoadmapHtml(data?.empty_state_message || "Chưa có dữ liệu")}</div>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="roadmap-detail-header">
      <div>
        <div class="finance-title">Kế Hoạch Học Tập Tự Động</div>
        <div class="roadmap-detail-subtitle">
          Danh sách đầu việc được tạo từ thông tin chat và lưu tạm trong application layer.
        </div>
      </div>
      <div class="roadmap-overview-pill">
        ${Number(data.total_completed_actions || 0)}/${Number(data.total_actions || 0)} đầu việc hoàn thành
      </div>
    </div>
    ${plans.map((plan) => renderRoadmapPlanBlock(plan)).join("")}
  `;
}

function renderRoadmapPlanBlock(plan) {
  const actions = Array.isArray(plan.actions) ? plan.actions : [];
  return `
    <section class="roadmap-plan-block">
      <div class="roadmap-plan-header">
        <div>
          <div class="roadmap-plan-title">${escapeRoadmapHtml(plan.topic)}</div>
          <div class="roadmap-plan-subtitle">
            ${escapeRoadmapHtml(plan.target_label)} | Còn ${Number(plan.days_remaining || 0)} ngày
          </div>
        </div>
        <div class="roadmap-plan-progress">${Number(plan.progress_percent || 0)}%</div>
      </div>

      <div class="roadmap-actions">
        ${actions
          .map(
            (action) => `
              <label class="roadmap-action-item">
                <input
                  type="checkbox"
                  data-plan-id="${escapeRoadmapHtml(plan.id)}"
                  data-action-id="${escapeRoadmapHtml(action.id)}"
                  ${action.completed ? "checked" : ""}
                />
                <div class="roadmap-action-content">
                  <div class="roadmap-action-title-row">
                    <span class="roadmap-action-title ${action.completed ? "is-completed" : ""}">
                      ${escapeRoadmapHtml(action.title)}
                    </span>
                    <span class="roadmap-action-due">${escapeRoadmapHtml(action.due_label)}</span>
                  </div>
                  <div class="roadmap-action-description">
                    ${escapeRoadmapHtml(action.description)}
                  </div>
                </div>
              </label>
            `
          )
          .join("")}
      </div>
    </section>
  `;
}

function formatRoadmapDate(value) {
  if (!value) {
    return "--";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleDateString("vi-VN");
}

function escapeRoadmapHtml(text) {
  return String(text ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
