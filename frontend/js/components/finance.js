
let financeState = {
  rendered: false,
  transactions: [],
  sortMode: "newest",
};

function renderFinancePage() {
  const container = document.getElementById("finance-page");
  if (!container) {
    return;
  }
  if (!financeState.rendered) {
    container.innerHTML = `
      <div class="finance-page">
        <div id="finance-summary" class="cards-row-3"></div>

        <div class="table-card">
          <div class="finance-toolbar">
            <div class="finance-title">Lịch Sử Giao Dịch Chi Tiết</div>
            <div class="finance-actions">
              <label class="finance-sort">
                <span>Sắp xếp theo</span>
                <select id="finance-sort-select">
                  <option value="newest" selected>Mới nhất</option>
                  <option value="oldest">Cũ nhất</option>
                  <option value="amount_desc">Số tiền: cao → thấp</option>
                  <option value="amount_asc">Số tiền: thấp → cao</option>
                </select>
              </label>
              <button id="finance-add-button" class="btn-add-transaction" type="button">
                <i class="fa-solid fa-plus"></i>
                Thêm Khoản Thu/Chi
              </button>
            </div>
          </div>

          <div class="finance-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Ngày</th>
                  <th>Danh Mục</th>
                  <th>Mô Tả Giao Dịch</th>
                  <th>Loại</th>
                  <th style="text-align:right">Số Tiền</th>
                </tr>
              </thead>
              <tbody id="finance-rows"></tbody>
            </table>
            <div id="finance-empty" class="finance-empty" style="display:none">
              Chưa có giao dịch. Hãy thêm khoản thu/chi đầu tiên.
            </div>
          </div>
        </div>

        <div id="finance-modal" class="modal-overlay" style="display:none">
          <div class="modal-card" role="dialog" aria-modal="true">
            <div class="modal-header">
              <div class="modal-title">Thêm Khoản Thu/Chi</div>
              <button id="finance-modal-close" class="modal-close" type="button">
                <i class="fa-solid fa-xmark"></i>
              </button>
            </div>

            <form id="finance-form" class="modal-body">
              <div class="form-grid">
                <div class="form-group">
                  <label for="tx-date">Ngày</label>
                  <input id="tx-date" type="date" required />
                </div>

                <div class="form-group">
                  <label for="tx-type">Loại</label>
                  <select id="tx-type" required>
                    <option value="income">Thu Nhập</option>
                    <option value="expense">Chi Tiêu</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="tx-category">Danh mục</label>
                  <input id="tx-category" type="text" placeholder="Ví dụ: Ăn uống, Học tập..." />
                </div>

                <div class="form-group">
                  <label for="tx-amount">Số tiền (VND)</label>
                  <input id="tx-amount" type="number" min="1" step="1" required placeholder="Ví dụ: 50000" />
                </div>

                <div class="form-group form-group-full">
                  <label for="tx-desc">Mô tả giao dịch</label>
                  <input id="tx-desc" type="text" placeholder="Ví dụ: Mua sách giáo trình..." />
                </div>
              </div>

              <div class="modal-footer">
                <button id="finance-cancel" class="btn-secondary" type="button">Hủy</button>
                <button id="finance-submit" class="btn-primary" type="submit">
                  Lưu giao dịch
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    `;
    bindFinanceEvents();
    financeState.rendered = true;
  }
  refreshFinanceData();
}

function bindFinanceEvents() {
  const addBtn = document.getElementById("finance-add-button");
  const modal = document.getElementById("finance-modal");
  const closeBtn = document.getElementById("finance-modal-close");
  const cancelBtn = document.getElementById("finance-cancel");
  const form = document.getElementById("finance-form");
  const sortSelect = document.getElementById("finance-sort-select");

  if (addBtn && modal) {
    addBtn.addEventListener("click", () => openFinanceModal());
  }
  if (closeBtn) {
    closeBtn.addEventListener("click", () => closeFinanceModal());
  }
  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => closeFinanceModal());
  }
  if (modal) {
    modal.addEventListener("click", (event) => {
      if (event.target === modal) {
        closeFinanceModal();
      }
    });
  }
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeFinanceModal();
    }
  });

  if (sortSelect) {
    sortSelect.addEventListener("change", () => {
      financeState.sortMode = String(sortSelect.value || "newest");
      renderFinanceTransactions(financeState.transactions);
    });
  }

  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      await submitFinanceForm();
    });
  }
}

function openFinanceModal() {
  const modal = document.getElementById("finance-modal");
  if (!modal) return;
  modal.style.display = "flex";

  const dateInput = document.getElementById("tx-date");
  const amountInput = document.getElementById("tx-amount");
  if (dateInput && !dateInput.value) {
    dateInput.valueAsDate = new Date();
  }
  if (amountInput) {
    amountInput.focus();
  }
}

function closeFinanceModal() {
  const modal = document.getElementById("finance-modal");
  if (!modal) return;
  modal.style.display = "none";
  const form = document.getElementById("finance-form");
  if (form) {
    form.reset();
  }
}

async function submitFinanceForm() {
  const dateEl = document.getElementById("tx-date");
  const typeEl = document.getElementById("tx-type");
  const categoryEl = document.getElementById("tx-category");
  const amountEl = document.getElementById("tx-amount");
  const descEl = document.getElementById("tx-desc");
  const submitBtn = document.getElementById("finance-submit");

  if (!dateEl || !typeEl || !amountEl) {
    return;
  }
  const payload = {
    transaction_type: String(typeEl.value),
    amount: Number(amountEl.value),
    category: categoryEl ? categoryEl.value.trim() || null : null,
    date: dateEl.value || null,
    merchant: null,
    description: descEl ? descEl.value.trim() || null : null,
    payment_method: null,
  };

  if (!payload.amount || payload.amount <= 0 || Number.isNaN(payload.amount)) {
    return;
  }
  if (submitBtn) submitBtn.disabled = true;
  try {
    await createTransaction(payload);
    closeFinanceModal();
    await refreshFinanceData();
  } catch (e) {
    console.error(e);
  } finally {
    if (submitBtn) submitBtn.disabled = false;
  }
}

async function refreshFinanceData() {
  await Promise.all([refreshFinanceSummary(), refreshFinanceTransactions()]);
}

async function refreshFinanceTransactions() {
  try {
    const transactions = await getTransactions();
    financeState.transactions = Array.isArray(transactions) ? transactions : [];
    renderFinanceTransactions(financeState.transactions);
  } catch (e) {
    console.error(e);
  }
}

async function refreshFinanceSummary() {
  const now = new Date();
  const month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  try {
    const summary = await getMonthlySummary(month);
    renderFinanceSummary(summary);
  } catch (e) {
    console.error(e);
    renderFinanceSummary(null);
  }
}

function renderFinanceSummary(summary) {
  const container = document.getElementById("finance-summary");
  if (!container) return;

  const income = summary?.total_monthly_income ?? null;
  const expense = summary?.total_monthly_expense ?? null;
  const contingency = summary?.total_contingency_money ?? null;

  container.innerHTML = `
    <div class="stat-card">
      <div class="card-top">
        <span>Tổng Thu Nhập Tháng</span>
        <div class="stat-icon icon-green">
          <i class="fa-solid fa-arrow-trend-up"></i>
        </div>
      </div>
      <div class="stat-num finance-num-green">${formatVnd(income)}</div>
    </div>

    <div class="stat-card">
      <div class="card-top">
        <span>Tổng Chi Tiêu Tháng</span>
        <div class="stat-icon icon-red">
          <i class="fa-solid fa-arrow-trend-down"></i>
        </div>
      </div>
      <div class="stat-num finance-num-red">${formatVnd(expense)}</div>
    </div>

    <div class="stat-card">
      <div class="card-top">
        <span>Tổng Tiền Dự Phòng</span>
        <div class="stat-icon icon-blue">
          <i class="fa-solid fa-piggy-bank"></i>
        </div>
      </div>
      <div class="stat-num">${formatVnd(contingency)}</div>
    </div>
  `;
}

function renderFinanceTransactions(transactions) {
  const tbody = document.getElementById("finance-rows");
  const empty = document.getElementById("finance-empty");
  if (!tbody || !empty) return;

  const sorted = sortTransactions(transactions, financeState.sortMode);
  tbody.innerHTML = "";
  if (!sorted.length) {
    empty.style.display = "block";
    return;
  }
  empty.style.display = "none";
  sorted.forEach((t) => {
    const tr = document.createElement("tr");
    const isExpense = t.transaction_type === "expense";
    const tagClass = isExpense ? "tag-expense" : "tag-income";
    const amountClass = isExpense ? "amount-expense" : "amount-income";
    const amountPrefix = isExpense ? "-" : "+";
    tr.innerHTML = `
      <td>${escapeHtml(t.date || "--")}</td>
      <td>${escapeHtml(t.category || "--")}</td>
      <td>${escapeHtml(t.description || "--")}</td>
      <td><span class="${tagClass}">${isExpense ? "Chi Tiêu" : "Thu Nhập"}</span></td>
      <td class="${amountClass}" style="text-align:right">${amountPrefix}${formatVnd(t.amount)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function sortTransactions(transactions, mode) {
  const list = Array.isArray(transactions) ? transactions.slice() : [];
  const dateKey = (t) => {
    const s = String(t?.date || "");
    const ts = Date.parse(s);
    return Number.isFinite(ts) ? ts : 0;
  };
  const amountKey = (t) => Number(t?.amount || 0);
  const idKey = (t) => Number(t?.id || 0);
  if (mode === "oldest") {
    return heapSort(list, (a, b) => {
      const d = dateKey(a) - dateKey(b);
      if (d !== 0) return d;
      return idKey(a) - idKey(b);
    });
  }
  if (mode === "amount_desc") {
    return heapSort(list, (a, b) => {
      const d = amountKey(a) - amountKey(b);
      if (d !== 0) return d;
      return idKey(a) - idKey(b);
    }).reverse();
  }
  if (mode === "amount_asc") {
    return heapSort(list, (a, b) => {
      const d = amountKey(a) - amountKey(b);
      if (d !== 0) return d;
      return idKey(a) - idKey(b);
    });
  }
  return heapSort(list, (a, b) => {
    const d = dateKey(a) - dateKey(b);
    if (d !== 0) return d;
    return idKey(a) - idKey(b);
  }).reverse();
}

function heapSort(arr, compare) {
  const a = arr.slice();
  const n = a.length;
  const swap = (i, j) => {
    const temp = a[i];
    a[i] = a[j];
    a[j] = temp;
  };
  const siftDown = (i, heapSize) => {
    while (true) {
      let largest = i;
      const left = 2 * i + 1;
      const right = 2 * i + 2;
      if (left < heapSize && compare(a[left], a[largest]) > 0) {
        largest = left;
      }
      if (right < heapSize && compare(a[right], a[largest]) > 0) {
        largest = right;
      }
      if (largest === i) break;
      swap(i, largest);
      i = largest;
    }
  };

  for (let i = Math.floor(n / 2) - 1; i >= 0; i--) {
    siftDown(i, n);
  }
  for (let end = n - 1; end > 0; end--) {
    swap(0, end);
    siftDown(0, end);
  }
  return a;
}

function formatVnd(amount) {
  if (amount == null || amount === "" || Number.isNaN(Number(amount))) {
    return "--";
  }
  const value = Math.round(Number(amount));
  return new Intl.NumberFormat("vi-VN").format(value) + " VNĐ";
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

