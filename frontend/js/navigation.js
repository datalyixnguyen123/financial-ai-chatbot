

function switchPage(pageId, linkEl) {
  const normalizedId = String(pageId || "").startsWith("page-")
    ? String(pageId)
    : `page-${pageId}`;

  const pages = document.querySelectorAll(".page-tab");
  pages.forEach((page) => {
    page.classList.remove("active-tab");
  });

  const targetPage = document.getElementById(normalizedId);
  if (targetPage) {
    targetPage.classList.add("active-tab");
  }

  const links = document.querySelectorAll(".menu-link");
  links.forEach((el) => el.classList.remove("active"));
  if (linkEl && typeof linkEl.classList !== "undefined") {
    linkEl.classList.add("active");
  }

  const headerText = document.getElementById("header-text");
  if (headerText) {
    const mapping = {
      "page-home": "Trang Chủ Bảng Điều Khiển",
      "page-finance": "Quản Lý Sổ Thu Chi Sinh Viên",
      "page-roadmap": "Lộ Trình Ôn Thi",
      "page-agent": "Trợ Lý Ảo Virtual Agent",
      "page-settings": "Cài Đặt",
    };
    headerText.textContent = mapping[normalizedId] || "FinStudy AI";
  }

  if (normalizedId === "page-finance" && typeof renderFinancePage === "function") {
    renderFinancePage();
  }
  if (normalizedId === "page-roadmap" && typeof renderRoadmapPage === "function") {
    renderRoadmapPage();
  }
}
