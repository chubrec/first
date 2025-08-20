"use strict";

// Простое хранилище состояния с локальным сохранением
const STORAGE_KEY = "smeta-app-state-v1";

/** @typedef {{
 *  id: string,
 *  name: string,
 *  description: string,
 *  unit: string,
 *  quantity: number,
 *  unitPrice: number,
 *  discountPercent: number,
 *  discountAmount: number,
 *  vatPercent: number
 * }} EstimateItem
 */

/** @typedef {{
 *  company: { name: string, tax: string, address: string, phone: string, email: string },
 *  client: { name: string, contact: string, address: string },
 *  estimate: { number: string, date: string, projectName: string, projectAddress: string, currency: string, vatRate: number, vatIncluded: boolean, validDays: number },
 *  items: EstimateItem[],
 *  customFields: { key: string, value: string }[],
 *  notes: string,
 *  terms: string
 * }} AppState
 */

/** @type {AppState} */
let state = {
  company: { name: "", tax: "", address: "", phone: "", email: "" },
  client: { name: "", contact: "", address: "" },
  estimate: {
    number: "",
    date: new Date().toISOString().slice(0, 10),
    projectName: "",
    projectAddress: "",
    currency: "RUB",
    vatRate: 20,
    vatIncluded: false,
    validDays: 30,
  },
  items: [],
  customFields: [],
  notes: "",
  terms: "",
};

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object") {
      state = Object.assign({}, state, parsed);
    }
  } catch (err) {
    console.error("Load state error", err);
  }
}

function saveState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (err) {
    console.error("Save state error", err);
  }
}

function generateId(prefix) {
  return `${prefix}_${Math.random().toString(36).slice(2, 9)}`;
}

function formatMoney(value) {
  const { currency } = state.estimate;
  try {
    return new Intl.NumberFormat("ru-RU", { style: "currency", currency }).format(value || 0);
  } catch {
    return (value || 0).toFixed(2);
  }
}

function parseNumber(value) {
  const num = parseFloat(String(value).replace(",", "."));
  return Number.isFinite(num) ? num : 0;
}

// Рендер пользовательских полей
function renderCustomFields() {
  const container = document.getElementById("custom-fields");
  container.innerHTML = "";
  state.customFields.forEach((cf, index) => {
    const row = document.createElement("div");
    row.className = "custom-field";
    row.innerHTML = `
      <span>${cf.key}</span>
      <input data-cf-index="${index}" class="cf-value" value="${cf.value || ""}" />
      <button class="btn remove" data-remove-cf="${index}">Удалить</button>
    `;
    container.appendChild(row);
  });
}

// Рендер таблицы позиций
function renderItems() {
  const body = document.getElementById("items-body");
  body.innerHTML = "";
  state.items.forEach((item, index) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${index + 1}</td>
      <td><input data-id="${item.id}" data-field="name" placeholder="Позиция" value="${item.name || ""}"></td>
      <td><input data-id="${item.id}" data-field="description" placeholder="Описание" value="${item.description || ""}"></td>
      <td><input data-id="${item.id}" data-field="unit" placeholder="шт, м, м²" value="${item.unit || ""}"></td>
      <td><input data-id="${item.id}" data-field="quantity" type="number" step="0.0001" value="${item.quantity}"></td>
      <td><input data-id="${item.id}" data-field="unitPrice" type="number" step="0.01" value="${item.unitPrice}"></td>
      <td><input data-id="${item.id}" data-field="discountPercent" type="number" step="0.01" min="0" value="${item.discountPercent}"></td>
      <td><input data-id="${item.id}" data-field="discountAmount" type="number" step="0.01" min="0" value="${item.discountAmount}"></td>
      <td><input data-id="${item.id}" data-field="vatPercent" type="number" step="0.01" min="0" value="${item.vatPercent}"></td>
      <td class="cell-sum" id="sum-${item.id}">${formatMoney(calcItemTotal(item))}</td>
      <td style="width:48px"><button class="btn-icon" data-remove-item="${item.id}">✕</button></td>
    `;
    body.appendChild(tr);
  });
}

function calcItemTotal(item) {
  const quantity = parseNumber(item.quantity);
  const unitPrice = parseNumber(item.unitPrice);
  const base = quantity * unitPrice;
  const discountFromPercent = base * (parseNumber(item.discountPercent) / 100);
  const discountAbs = parseNumber(item.discountAmount);
  const discount = Math.max(discountFromPercent, discountAbs);
  const afterDiscount = Math.max(base - discount, 0);
  const vatPercent = Number.isFinite(parseNumber(item.vatPercent)) ? parseNumber(item.vatPercent) : state.estimate.vatRate;
  const vatIncluded = !!state.estimate.vatIncluded;
  if (vatIncluded) {
    const divisor = 1 + (vatPercent / 100);
    return afterDiscount; // сумма уже с НДС
  } else {
    return afterDiscount * (1 + vatPercent / 100);
  }
}

function calcSummary() {
  let subtotal = 0;
  let discountTotal = 0;
  let vatTotal = 0;

  const vatIncluded = !!state.estimate.vatIncluded;

  state.items.forEach((item) => {
    const quantity = parseNumber(item.quantity);
    const unitPrice = parseNumber(item.unitPrice);
    const base = quantity * unitPrice;
    const discountFromPercent = base * (parseNumber(item.discountPercent) / 100);
    const discountAbs = parseNumber(item.discountAmount);
    const discount = Math.max(discountFromPercent, discountAbs);
    const afterDiscount = Math.max(base - discount, 0);
    const vatPercent = Number.isFinite(parseNumber(item.vatPercent)) ? parseNumber(item.vatPercent) : state.estimate.vatRate;

    if (vatIncluded) {
      const net = afterDiscount / (1 + vatPercent / 100);
      const vat = afterDiscount - net;
      subtotal += net;
      discountTotal += discount; // уже учтено в afterDiscount
      vatTotal += vat;
    } else {
      const vat = afterDiscount * (vatPercent / 100);
      subtotal += afterDiscount;
      discountTotal += discount;
      vatTotal += vat;
    }
  });

  const total = subtotal + vatTotal;
  return { subtotal, discountTotal, vatTotal, total };
}

function updateSummaryUI() {
  const sums = calcSummary();
  document.getElementById("sum-subtotal").textContent = formatMoney(sums.subtotal);
  document.getElementById("sum-discount").textContent = formatMoney(sums.discountTotal);
  document.getElementById("sum-vat").textContent = formatMoney(sums.vatTotal);
  document.getElementById("sum-total").textContent = formatMoney(sums.total);
}

function rerender() {
  renderCustomFields();
  renderItems();
  updateSummaryUI();
}

function bindHeader() {
  document.getElementById("btn-new").addEventListener("click", () => {
    if (confirm("Очистить текущую смету?")) {
      state.items = [];
      state.customFields = [];
      state.notes = "";
      state.terms = "";
      saveState();
      rerender();
      bindFormValues();
    }
  });

  document.getElementById("btn-save").addEventListener("click", () => {
    saveState();
    alert("Сохранено в браузере");
  });

  document.getElementById("btn-export").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const name = state.estimate.number || `smeta-${new Date().toISOString().slice(0,10)}`;
    a.href = url;
    a.download = `${name}.json`;
    a.click();
    URL.revokeObjectURL(url);
  });

  document.getElementById("file-import").addEventListener("change", (e) => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const data = JSON.parse(String(reader.result));
        state = Object.assign({}, state, data);
        saveState();
        rerender();
        bindFormValues();
      } catch (err) {
        alert("Не удалось импортировать файл");
      }
    };
    reader.readAsText(file);
  });

  document.getElementById("btn-print").addEventListener("click", () => {
    window.print();
  });
}

function bindFormValues() {
  // Company
  document.getElementById("company-name").value = state.company.name || "";
  document.getElementById("company-tax").value = state.company.tax || "";
  document.getElementById("company-address").value = state.company.address || "";
  document.getElementById("company-phone").value = state.company.phone || "";
  document.getElementById("company-email").value = state.company.email || "";

  // Client
  document.getElementById("client-name").value = state.client.name || "";
  document.getElementById("client-contact").value = state.client.contact || "";
  document.getElementById("client-address").value = state.client.address || "";

  // Estimate
  document.getElementById("estimate-number").value = state.estimate.number || "";
  document.getElementById("estimate-date").value = state.estimate.date || new Date().toISOString().slice(0, 10);
  document.getElementById("project-name").value = state.estimate.projectName || "";
  document.getElementById("project-address").value = state.estimate.projectAddress || "";
  document.getElementById("currency-select").value = state.estimate.currency || "RUB";
  document.getElementById("vat-rate").value = String(state.estimate.vatRate ?? 20);
  document.getElementById("vat-included").value = state.estimate.vatIncluded ? "yes" : "no";
  document.getElementById("valid-days").value = String(state.estimate.validDays ?? 30);

  // Notes
  document.getElementById("notes").value = state.notes || "";
  document.getElementById("terms").value = state.terms || "";
}

function bindFormEvents() {
  // Company fields
  document.getElementById("company-name").addEventListener("input", (e) => { state.company.name = e.target.value; saveState(); });
  document.getElementById("company-tax").addEventListener("input", (e) => { state.company.tax = e.target.value; saveState(); });
  document.getElementById("company-address").addEventListener("input", (e) => { state.company.address = e.target.value; saveState(); });
  document.getElementById("company-phone").addEventListener("input", (e) => { state.company.phone = e.target.value; saveState(); });
  document.getElementById("company-email").addEventListener("input", (e) => { state.company.email = e.target.value; saveState(); });

  // Client fields
  document.getElementById("client-name").addEventListener("input", (e) => { state.client.name = e.target.value; saveState(); });
  document.getElementById("client-contact").addEventListener("input", (e) => { state.client.contact = e.target.value; saveState(); });
  document.getElementById("client-address").addEventListener("input", (e) => { state.client.address = e.target.value; saveState(); });

  // Estimate fields
  document.getElementById("estimate-number").addEventListener("input", (e) => { state.estimate.number = e.target.value; saveState(); });
  document.getElementById("estimate-date").addEventListener("input", (e) => { state.estimate.date = e.target.value; saveState(); });
  document.getElementById("project-name").addEventListener("input", (e) => { state.estimate.projectName = e.target.value; saveState(); });
  document.getElementById("project-address").addEventListener("input", (e) => { state.estimate.projectAddress = e.target.value; saveState(); });
  document.getElementById("currency-select").addEventListener("change", (e) => { state.estimate.currency = e.target.value; saveState(); updateSummaryUI(); });
  document.getElementById("vat-rate").addEventListener("input", (e) => { state.estimate.vatRate = parseNumber(e.target.value); saveState(); updateSummaryUI(); });
  document.getElementById("vat-included").addEventListener("change", (e) => { state.estimate.vatIncluded = e.target.value === "yes"; saveState(); updateSummaryUI(); });
  document.getElementById("valid-days").addEventListener("input", (e) => { state.estimate.validDays = parseInt(e.target.value || "0", 10); saveState(); });

  // Notes
  document.getElementById("notes").addEventListener("input", (e) => { state.notes = e.target.value; saveState(); });
  document.getElementById("terms").addEventListener("input", (e) => { state.terms = e.target.value; saveState(); });

  // Custom fields add/remove
  document.getElementById("btn-add-custom").addEventListener("click", () => {
    const key = document.getElementById("custom-key").value.trim();
    const value = document.getElementById("custom-value").value.trim();
    if (!key) return;
    state.customFields.push({ key, value });
    document.getElementById("custom-key").value = "";
    document.getElementById("custom-value").value = "";
    saveState();
    renderCustomFields();
  });

  document.getElementById("custom-fields").addEventListener("input", (e) => {
    const indexStr = e.target.getAttribute("data-cf-index");
    if (!indexStr) return;
    const index = parseInt(indexStr, 10);
    if (!Number.isFinite(index)) return;
    state.customFields[index].value = e.target.value;
    saveState();
  });

  document.getElementById("custom-fields").addEventListener("click", (e) => {
    const idx = e.target.getAttribute("data-remove-cf");
    if (idx == null) return;
    const index = parseInt(idx, 10);
    state.customFields.splice(index, 1);
    saveState();
    renderCustomFields();
  });

  // Items
  document.getElementById("btn-add-item").addEventListener("click", () => {
    state.items.push({
      id: generateId("item"),
      name: "",
      description: "",
      unit: "шт",
      quantity: 1,
      unitPrice: 0,
      discountPercent: 0,
      discountAmount: 0,
      vatPercent: state.estimate.vatRate,
    });
    saveState();
    renderItems();
    updateSummaryUI();
  });

  document.getElementById("btn-clear-items").addEventListener("click", () => {
    if (confirm("Удалить все позиции?")) {
      state.items = [];
      saveState();
      renderItems();
      updateSummaryUI();
    }
  });

  document.getElementById("items-body").addEventListener("input", (e) => {
    const id = e.target.getAttribute("data-id");
    const field = e.target.getAttribute("data-field");
    if (!id || !field) return;
    const item = state.items.find((it) => it.id === id);
    if (!item) return;
    if (["quantity","unitPrice","discountPercent","discountAmount","vatPercent"].includes(field)) {
      item[field] = parseNumber(e.target.value);
    } else {
      item[field] = e.target.value;
    }
    saveState();
    // Обновляем сумму по строке
    const cell = document.getElementById(`sum-${id}`);
    if (cell) cell.textContent = formatMoney(calcItemTotal(item));
    updateSummaryUI();
  });

  document.getElementById("items-body").addEventListener("click", (e) => {
    const removeId = e.target.getAttribute("data-remove-item");
    if (!removeId) return;
    state.items = state.items.filter((it) => it.id !== removeId);
    saveState();
    renderItems();
    updateSummaryUI();
  });
}

function init() {
  loadState();
  bindHeader();
  rerender();
  bindFormValues();
  bindFormEvents();
  // Если нет позиций — создадим одну для удобства
  if (state.items.length === 0) {
    document.getElementById("btn-add-item").click();
  }
}

document.addEventListener("DOMContentLoaded", init);

