

function renderWelcomeScreen() {
  const container = document.getElementById("welcome-screen");

  if (!container) {
    console.error("Welcome screen container not found.");
    return;
  }
  container.innerHTML = `
    <div class="welcome-card">
      <div class="welcome-logo">
        <i class="fa-solid fa-leaf"></i>
      </div>

      <div class="welcome-badge">
        <i class="fa-solid fa-sparkles"></i>
        FinStudy AI - Người Bạn Đồng Hành Cùng Genz
      </div>

      <h1 class="welcome-title">
        Học Tập Vững Vàng, <span>Tài Chính Thong Dong</span>
      </h1>

      <p class="welcome-quote">
        "Chúc bạn có một hành trình đại học thật rực rỡ! Hãy để AI cân bằng
        nỗi lo chi tiêu và tối ưu lộ trình học tập, giúp bạn tự tin chạm tay
        đến những điểm số cao nhất!"
      </p>

      <!-- LỜI HỨA CỦA FINSTUDY AI -->
      <div class="promises-grid">
        <div class="promise-item">
          <div
            class="promise-icon"
            style="background: #dcfce7; color: var(--primary-emerald)"
          >
            <i class="fa-solid fa-wallet"></i>
          </div>

          <div class="promise-title">Không Bao Giờ Trễ Hạn</div>

          <div class="promise-desc">
            Cam kết giúp bạn quản lý từng đồng sinh hoạt phí, không còn nỗi lo tài chính kéo dài!
          </div>
        </div>

        <div class="promise-item">
          <div
            class="promise-icon"
            style="background: #dbeafe; color: var(--primary-blue)"
          >
            <i class="fa-solid fa-graduation-cap"></i>
          </div>

          <div class="promise-title">Tối Ưu Điểm Số GPA</div>

          <div class="promise-desc">
            Lên lịch ôn thi thông minh theo phương pháp Pomodoro cá nhân hóa.
          </div>
        </div>

        <div class="promise-item">
          <div
            class="promise-icon"
            style="background: #fef3c7; color: #d97706"
          >
            <i class="fa-solid fa-shield-halved"></i>
          </div>

          <div class="promise-title">Bảo Mật & Tin Cậy</div>

          <div class="promise-desc">
            Trợ lý AI đồng hành 24/7, lắng nghe và tối ưu theo từng mục
            tiêu của bạn.
          </div>
        </div>

      </div>

      <button class="btn-enter" onclick="enterDashboard()">
        Bắt Đầu Khám Phá
        <i class="fa-solid fa-arrow-right"></i>
      </button>
    </div>
  `;
}

function enterDashboard() {
  const welcomeScreen = document.getElementById("welcome-screen");
  const appContainer = document.getElementById("app-container");

  if (!welcomeScreen || !appContainer) {
    console.error("Welcome screen or app container not found.");
    return;
  }
  welcomeScreen.classList.add("hidden");
  appContainer.classList.add("active");
}