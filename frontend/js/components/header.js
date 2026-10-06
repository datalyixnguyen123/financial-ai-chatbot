
function renderHeader() {
  const container = document.getElementById("app-header");
  if (!container) {
    console.error("Header container not found.");
    return;
  }
  container.innerHTML = `
    <header class="header-bar">
      <div class="header-title">
        <h1 id="header-text">Trang Chủ Bảng Điều Khiển</h1>
        <p>
          Hệ thống AI Cá Nhân Hóa Tài Chính & Lộ Trình Học Tập Cho Sinh viên
        </p>
      </div>

      <div class="profile-card">
        <div class="avatar-img">SV</div>
        
        <div style="font-size: 0.85rem">
          <div style="font-weight: 700">
            Sinh Viên Demo
          </div>

          <div style="color: var(--text-muted); font-size: 0.75rem">
            Mục tiêu GPA: 3.6
          </div>
        </div>
      </div>
    </header>
  `;
}