

function renderHomeSummary(data = {}) {
  const container = document.getElementById("home-summary");
  if (!container) {
    console.error("Home summary container not found.");
    return;
  }

  const {
    weeklyBudget = null,
    upcomingStudy = null,
  } = data;

  container.innerHTML = `
    <div class="cards-row">
      <!-- WEEKLY BUDGET -->
      <div class="stat-card">
        <div class="card-top">

          <span>Ngân Sách Chi Tiêu Tuần</span>

          <div class="stat-icon icon-green">
            <i class="fa-solid fa-coins"></i>
          </div>
        </div>

        <div class="stat-num">
          ${weeklyBudget?.amount ?? "--"}
        </div>

        <span class="pill-badge pill-green">
          ${weeklyBudget?.label ?? "Chưa có dữ liệu"}
        </span>
      </div>

      <!-- UPCOMING STUDY -->
      <div class="stat-card">
        <div class="card-top">

          <span>Lịch Ôn Thi Sắp Tới</span>

          <div class="stat-icon icon-blue">
            <i class="fa-solid fa-book-open"></i>
          </div>
        </div>
        <div class="stat-num">
          ${upcomingStudy?.subject ?? "--"}
        </div>
        <span class="pill-badge pill-blue">
          ${upcomingStudy?.label ?? "Chưa có dữ liệu"}
        </span>
      </div>
    </div>
  `;
}