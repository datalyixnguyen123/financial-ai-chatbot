


function renderSidebar() {
  const container = document.getElementById("app-sidebar");

  if (!container) {
    console.error("Sidebar container not found.");
    return;
  }

  container.innerHTML = `
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-logo">
          <i class="fa-solid fa-leaf"></i>
        </div>

        <div class="brand-name">FinStudy AI</div>
      </div>

      <ul class="menu-list">
        <li class="menu-item">
          <a
            class="menu-link active"
            onclick="switchPage('page-home', this)"
          >
            <i class="fa-solid fa-house"></i>
            Trang Chủ
          </a>
        </li>
        <li class="menu-item">
          <a
            class="menu-link"
            onclick="switchPage('page-finance', this)"
          >
            <i class="fa-solid fa-wallet"></i>
            Quản Lý Sổ Thu Chi
          </a>
        </li>

        <li class="menu-item">
          <a
            class="menu-link"
            onclick="switchPage('page-roadmap', this)"
          >
            <i class="fa-solid fa-graduation-cap"></i>
            Lộ Trình Ôn Thi
          </a>
        </li>

        <li class="menu-item">
          <a
            class="menu-link"
            onclick="switchPage('page-agent', this)"
          >
            <i class="fa-solid fa-robot"></i>
            Trợ Lý Ảo Virtual Agent
          </a>
        </li>

        <li class="menu-item">
          <a
            class="menu-link"
            onclick="switchPage('page-settings', this)"
          >
            <i class="fa-solid fa-gear"></i>
            Cài Đặt
          </a>
        </li>
      </ul>
    </aside>
  `;
}