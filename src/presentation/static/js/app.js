(function () {
  "use strict";

  const PAGE_SIZE = 60;
  const I18N = window.I18N || {};

  function t(key, fallback) {
    if (I18N && I18N[key]) return I18N[key];
    return fallback !== undefined ? fallback : key;
  }

  const STATUS_LABEL = {
    encontrado: t("filter_status_found", "PDF encontrado"),
    no_encontrado: t("filter_status_missing", "PDF no encontrado"),
    posible: t("filter_status_possible", "Posible coincidencia"),
    vacio: t("filter_status_empty", "Sin nº de documento"),
  };

  let DATA = null;
  let records = [];
  let filtered = [];
  let page = 0;
  let sortKey = "fecha";
  let sortDir = -1;
  let selectedId = null;
  let extraFilter = null;
  let searchHistory = [];
  let viewCounts = {};

  const $ = (sel) => document.querySelector(sel);

  // =========================================================================
  // STATELESS HELPER FUNCTIONS (CLIENT-SIDE)
  // =========================================================================

  function stripAccents(s) {
    return (s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }
  function normText(s) {
    return stripAccents(String(s || ""))
      .toLowerCase()
      .replace(/[^a-z0-9%.,/\- ]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function bigrams(s) {
    const out = new Set();
    for (let i = 0; i < s.length - 1; i++) out.add(s.substring(i, i + 2));
    return out;
  }
  function diceCoefficient(a, b) {
    const A = bigrams(a), B = bigrams(b);
    if (!A.size || !B.size) return 0;
    let inter = 0;
    for (const g of A) if (B.has(g)) inter++;
    return (2 * inter) / (A.size + B.size);
  }

  function fmtMoney(n) {
    if (n === null || n === undefined || n === "") return "";
    const v = Number(n);
    if (Number.isNaN(v)) return String(n);
    if (window.ExternalService && typeof window.ExternalService.convertFromPEN === "function") {
      const conv = window.ExternalService.convertFromPEN(v);
      return conv.formatted;
    }
    const locale = window.CURRENT_LANG === "en" ? "en-US" : "es-PE";
    return "S/ " + v.toLocaleString(locale, { minimumFractionDigits: 2, maximumFractionDigits: 4 });
  }

  // Hook para refresco reactivo cuando cambian las tasas o divisa externa
  window.onCurrencyChanged = function () {
    renderTable();
    if (selectedId) {
      const r = records.find((x) => x.id === selectedId);
      if (r) showDetail(r);
    }
  };
  window.onCurrencyRatesLoaded = function () {
    renderTable();
  };
  function fmtDate(s) {
    if (!s) return "(sin fecha)";
    return s;
  }
  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  // =========================================================================
  // APP LIFECYCLE & DATA LOADING
  // =========================================================================

  async function load() {
    let res;
    try {
      res = await fetch("/api/invoices/data", { cache: "no-store" });
      if (!res.ok) {
        res = await fetch("data.json", { cache: "no-store" });
      }
    } catch (e) {
      res = await fetch("data.json", { cache: "no-store" });
    }

    if (!res || !res.ok) {
      $("#sourceInfo").textContent = t("loading_data", "No se pudo cargar los datos de facturas.");
      return;
    }
    DATA = await res.json();
    records = DATA.registros || [];
    searchHistory = DATA.search_history || [];

    const sourceTpl = t("source_label", "Fuente: {source} — hoja \"{sheet}\" — generado {generated}");
    $("#sourceInfo").textContent = sourceTpl
      .replace("{source}", DATA.fuente_excel || "Excel Maestro")
      .replace("{sheet}", DATA.hoja || "Detalle facturas")
      .replace("{generated}", DATA.generado || "recientemente");

    fillProveedorOptions();
    renderCards();
    renderInconsistencies();
    renderHistoryChips();
    applyFilters();
    wireEvents();
    if (new URLSearchParams(window.location.search).get("select") === "1" && records.length > 0) {
      setTimeout(() => selectRecord(records[0].id), 200);
    }
  }

  function fillProveedorOptions() {
    const sel = $("#fProveedor");
    for (const p of (DATA.proveedores || [])) {
      const opt = document.createElement("option");
      opt.value = p;
      opt.textContent = p;
      sel.appendChild(opt);
    }
  }

  function renderCards() {
    const i = DATA.indicadores || {};
    const cards = [
      { num: i.total_registros || 0, lbl: t("card_total_records", "Registros analizados") },
      { num: i.medicamentos_distintos || 0, lbl: t("card_distinct_meds", "Medicamentos distintos") },
      { num: i.pdfs_encontrados || 0, lbl: t("card_pdfs_found", "PDFs encontrados"), cls: "ok" },
      { num: i.pdfs_faltantes || 0, lbl: t("card_pdfs_missing", "PDFs faltantes"), cls: "bad" },
      { num: i.posibles_coincidencias || 0, lbl: t("card_possible_matches", "Posibles coincidencias"), cls: "warn" },
      { num: i.registros_sin_documento || 0, lbl: t("card_no_doc_number", "Registros sin nº de documento") },
      { num: (i.pct_vinculados || 0) + "%", lbl: t("card_pct_linked", "% vinculados a un PDF") },
    ];
    $("#cards").innerHTML = cards
      .map(
        (c) => `<div class="card ${c.cls || ""}"><div class="num">${c.num}</div><div class="lbl">${c.lbl}</div></div>`
      )
      .join("");
  }

  function renderInconsistencies() {
    const inc = (DATA.indicadores && DATA.indicadores.inconsistencias) || DATA.inconsistencias || {};
    const items = [
      { key: "filas_duplicadas", label: t("inc_duplicate_rows", "Filas duplicadas"), filter: "duplicado" },
      { key: "medicamentos_sin_costo", label: t("inc_medicines_no_cost", "Medicamentos sin costo"), filter: "sin_costo" },
      { key: "fechas_invalidas", label: t("inc_invalid_dates", "Fechas vacías o inválidas"), filter: "fecha_invalida" },
      { key: "documentos_vacios", label: t("inc_empty_docs", "Sin número de documento"), filter: "vacio" },
      { key: "pdfs_faltantes", label: t("inc_missing_pdfs", "Archivos PDF faltantes"), filter: "no_encontrado" },
      { key: "posibles_coincidencias_multiples", label: t("inc_multiple_matches", "Con más de una posible coincidencia"), filter: "posible_multi" },
    ];
    $("#inconsList").innerHTML = items
      .map(
        (it) =>
          `<div class="inconsistency-item" data-filter="${it.filter}"><span>${it.label}</span><span class="n">${inc[it.key] || 0}</span></div>`
      )
      .join("");
    $("#inconsList").querySelectorAll(".inconsistency-item").forEach((el) => {
      el.addEventListener("click", () => {
        applyIncFilter(el.dataset.filter);
      });
    });
  }

  function renderHistoryChips() {
    const historyBox = $("#historyBox");
    if (!historyBox) return;
    if (!searchHistory.length) {
      historyBox.innerHTML = "";
      return;
    }
    const hTitle = t("history_title", "Historial de búsquedas recientes (Estado de Sesión - Stateful):");
    historyBox.innerHTML = `<div class="fuzzy-box" style="border-style: solid; border-color: #2a3b4a; background: #16212c;"><div class="fz-title">${escapeHtml(hTitle)}</div>` +
      searchHistory.map((q) => `<span class="fuzzy-chip history-chip" data-v="${escapeHtml(q)}" style="border-color: #4da3ff; color: #4da3ff;">🕒 ${escapeHtml(q)}</span>`).join("") +
      `</div>`;
    historyBox.querySelectorAll(".history-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        $("#qMed").value = chip.dataset.v;
        applyFilters();
      });
    });
  }

  function applyIncFilter(kind) {
    resetFiltersUI();
    switch (kind) {
      case "duplicado":
        extraFilter = { type: "duplicado" };
        break;
      case "sin_costo":
        extraFilter = { type: "sin_costo" };
        break;
      case "fecha_invalida":
        extraFilter = { type: "fecha_invalida" };
        break;
      case "vacio":
        $("#fEstado").value = "vacio";
        extraFilter = null;
        break;
      case "no_encontrado":
        $("#fEstado").value = "no_encontrado";
        extraFilter = null;
        break;
      case "posible_multi":
        extraFilter = { type: "posible_multi" };
        break;
    }
    page = 0;
    applyFilters();
    window.scrollTo({ top: document.querySelector(".panel:nth-of-type(2)").offsetTop - 10, behavior: "smooth" });
  }

  function resetFiltersUI() {
    $("#qMed").value = "";
    $("#fFechaDesde").value = "";
    $("#fFechaHasta").value = "";
    $("#fProveedor").value = "";
    $("#fEstado").value = "";
    $("#fDocumento").value = "";
    $("#fArchivo").value = "";
    extraFilter = null;
  }

  function currentFilters() {
    return {
      q: normText($("#qMed").value),
      qRaw: $("#qMed").value.trim(),
      qWords: normText($("#qMed").value).split(" ").filter(Boolean),
      fechaDesde: $("#fFechaDesde").value || null,
      fechaHasta: $("#fFechaHasta").value || null,
      proveedor: $("#fProveedor").value,
      estado: $("#fEstado").value,
      documento: normText($("#fDocumento").value),
      archivo: normText($("#fArchivo").value),
    };
  }

  function matchesRecord(r, f) {
    if (f.proveedor && r.proveedor !== f.proveedor) return false;
    if (f.estado && r.pdf_status !== f.estado) return false;
    if (f.fechaDesde && (!r.fecha || r.fecha < f.fechaDesde)) return false;
    if (f.fechaHasta && (!r.fecha || r.fecha > f.fechaHasta)) return false;
    if (f.documento) {
      const doc = normText(r.documento);
      if (!doc.includes(f.documento)) return false;
    }
    if (f.archivo) {
      const cands = (r.candidatos || r.pdf_candidates || []).map((c) => normText(typeof c === "string" ? c : c.path || ""));
      if (!cands.some((c) => c.includes(f.archivo))) return false;
    }
    if (f.qWords.length) {
      const p = normText(r.producto || "");
      if (!f.qWords.every((w) => p.includes(w))) return false;
    }
    if (extraFilter) {
      const probs = r.problemas || [];
      if (extraFilter.type === "duplicado" && !probs.includes("duplicado_excel") && !r.duplicado) return false;
      if (extraFilter.type === "sin_costo" && !probs.includes("sin_costo") && !r.sin_costo) return false;
      if (extraFilter.type === "fecha_invalida" && !probs.includes("fecha_invalida")) return false;
      if (extraFilter.type === "posible_multi" && !(r.pdf_status === "posible" && (r.candidatos || []).length > 1)) return false;
    }
    return true;
  }

  async function applyFilters() {
    const f = currentFilters();
    filtered = records.filter((r) => matchesRecord(r, f));
    sortFiltered();
    page = 0;
    renderFuzzy(f);
    renderTable();

    // Guardar búsqueda en sesión stateful del backend si hay texto
    if (f.qRaw) {
      try {
        const hRes = await fetch("/api/stateful/search-history", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: f.qRaw })
        });
        if (hRes.ok) {
          const hData = await hRes.json();
          searchHistory = hData.search_history || [];
          renderHistoryChips();
        }
      } catch (e) {}
    }
  }

  function sortFiltered() {
    filtered.sort((a, b) => {
      let av = a[sortKey], bv = b[sortKey];
      if (av === null || av === undefined) av = "";
      if (bv === null || bv === undefined) bv = "";
      if (typeof av === "number" || typeof bv === "number") {
        av = Number(av) || 0;
        bv = Number(bv) || 0;
      }
      if (av < bv) return -1 * sortDir;
      if (av > bv) return 1 * sortDir;
      return 0;
    });
  }

  function renderFuzzy(f) {
    const box = $("#fuzzyBox");
    if (!f.q || f.q.length < 3) {
      box.innerHTML = "";
      return;
    }
    const uniques = new Map();
    for (const r of records) {
      const pNorm = normText(r.producto);
      if (pNorm && !uniques.has(pNorm)) uniques.set(pNorm, r.producto);
    }
    const directHit = filtered.length > 0;
    const scored = [];
    for (const [norm, original] of uniques) {
      if (norm.includes(f.q)) continue;
      const score = diceCoefficient(f.q, norm);
      if (score >= 0.42) scored.push({ norm, original, score });
    }
    scored.sort((a, b) => b.score - a.score);
    const top = scored.slice(0, 8);
    if (!top.length) {
      const emptyTpl = t("fuzzy_empty", "No se encontraron coincidencias exactas ni variaciones cercanas para \"{query}\".");
      box.innerHTML = directHit
        ? ""
        : `<div class="fuzzy-box">${emptyTpl.replace("{query}", escapeHtml($("#qMed").value))}</div>`;
      return;
    }
    const fzTitle = t("fuzzy_title", "¿Quizás buscaba? (Sugerencias calculadas - Stateless):");
    box.innerHTML = `<div class="fuzzy-box"><div class="fz-title">${escapeHtml(fzTitle)}</div>` +
      top.map((t) => `<span class="fuzzy-chip" data-v="${escapeHtml(t.original)}">${escapeHtml(t.original)}</span>`).join("") +
      `</div>`;
    box.querySelectorAll(".fuzzy-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        $("#qMed").value = chip.dataset.v;
        applyFilters();
      });
    });
  }

  function renderTable() {
    const total = filtered.length;
    const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    if (page >= totalPages) page = totalPages - 1;
    const start = page * PAGE_SIZE;
    const pageItems = filtered.slice(start, start + PAGE_SIZE);

    const foundTpl = t("results_found", "{count} registro(s) encontrado(s)");
    $("#resultMeta").textContent = foundTpl.replace("{count}", total) +
      (extraFilter ? t("filter_active_issue", " — filtro de inconsistencia activo") : "");

    $("#tbody").innerHTML = pageItems
      .map((r) => {
        const cls = r.id === selectedId ? "selected" : "";
        return `<tr class="${cls}" data-id="${r.id}">
          <td>${escapeHtml(fmtDate(r.fecha))}</td>
          <td>${escapeHtml(r.proveedor || "")}</td>
          <td>${escapeHtml(r.documento || "")}</td>
          <td title="${escapeHtml(r.producto || "")}">${escapeHtml(r.producto || "")}</td>
          <td>${escapeHtml(r.cantidad ?? "")}</td>
          <td>${escapeHtml(r.um || "")}</td>
          <td>${fmtMoney(r.precio_unitario)}</td>
          <td>${fmtMoney(r.importe_total)}</td>
          <td>${fmtMoney(r.costo_unidad)}</td>
          <td><span class="badge ${r.pdf_status}">${STATUS_LABEL[r.pdf_status] || r.pdf_status}</span></td>
        </tr>`;
      })
      .join("");

    $("#tbody").querySelectorAll("tr").forEach((tr) => {
      tr.addEventListener("click", () => {
        const id = Number(tr.dataset.id);
        selectRecord(id);
      });
    });

    const pageTpl = t("page_info", "Página {current} de {total}");
    $("#pagerInfo").textContent = pageTpl.replace("{current}", page + 1).replace("{total}", totalPages);
    $("#btnPrev").disabled = page <= 0;
    $("#btnNext").disabled = page >= totalPages - 1;
  }

  async function selectRecord(id) {
    selectedId = id;
    const r = records.find((x) => x.id === id);
    if (!r) return;
    renderTable();

    // [STATEFUL 1] Registrar y actualizar contador de visualizaciones en el backend
    try {
      const vRes = await fetch(`/api/stateful/track-view/${id}`, { method: "POST" });
      if (vRes.ok) {
        const vData = await vRes.json();
        viewCounts[id] = vData.total_views;
      }
    } catch (e) {}

    showDetail(r);
  }

  function showDetail(r) {
    $("#detailPanel").style.display = "";
    const views = viewCounts[r.id] || 1;
    const viewsTpl = t("views_badge", "👁 {count} vista(s)");
    const viewsText = viewsTpl.replace("{count}", views);

    const kv = [
      [t("detail_med", "Medicamento"), r.producto],
      [t("detail_provider", "Proveedor"), r.proveedor],
      [t("detail_date", "Fecha factura"), r.fecha || "(sin fecha)"],
      [t("detail_doc", "N° factura"), r.documento || "(vacío)"],
      [t("detail_qty", "Cantidad"), `${r.cantidad ?? ""} ${r.um || ""}`],
      [t("detail_unit_price", "Precio unitario"), fmtMoney(r.precio_unitario)],
      [t("detail_total_amount", "Importe total"), fmtMoney(r.importe_total)],
      [t("detail_units_box", "Unidades/caja"), r.unidades_caja ?? ""],
      [t("detail_total_units", "Unidades totales"), r.unidades_totales ?? ""],
      [t("detail_unit_cost_stateless", "Costo por unidad (Stateless)"), fmtMoney(r.costo_unidad)],
      [t("detail_detection_method", "Método de detección"), r.metodo_deteccion || ""],
      [t("detail_views_stateful", "Visualizaciones (Stateful)"), `<span class="badge ok">${escapeHtml(viewsText)}</span>`],
      [t("detail_source_sheet", "Fuente (hoja original)"), r.fuente || ""],
      [t("detail_pdf_status", "Estado PDF"), `<span class="badge ${r.pdf_status}">${STATUS_LABEL[r.pdf_status]}</span> — ${escapeHtml(r.pdf_match_mode || "")}`],
    ];
    $("#detailKv").innerHTML = kv
      .map(([k, v]) => `<div class="k">${escapeHtml(k)}</div><div class="v">${typeof v === "string" && v.includes("<span") ? v : escapeHtml(v)}</div>`)
      .join("");

    const candArea = $("#candidatesArea");
    const rawCands = r.candidatos || r.pdf_candidates || [];
    const cands = rawCands.map((c) => (typeof c === "string" ? c : c.path || c.filename || ""));

    if (r.pdf_status === "posible" && cands.length > 1) {
      candArea.innerHTML = `<div class="hint">${escapeHtml(t("detail_multiple_matches", "Hay varias coincidencias posibles. Seleccione la correcta para previsualizar:"))}</div>
        <div class="candidate-list">${cands
          .map((c) => `<button class="small cand-btn" data-p="${escapeHtml(c)}">${escapeHtml(c.split("/").pop())}</button>`)
          .join("")}</div>`;
      candArea.querySelectorAll(".cand-btn").forEach((b) => {
        b.addEventListener("click", () => showPdf(b.dataset.p));
      });
    } else {
      candArea.innerHTML = "";
    }

    if (cands.length >= 1) {
      showPdf(cands[0]);
    } else if (r.pdf_rel) {
      showPdf(r.pdf_rel);
    } else {
      showPdfEmpty(r.pdf_status);
    }
  }

  function showPdfEmpty(status) {
    const msg = status === "vacio"
      ? t("detail_empty_no_doc", "Este registro no tiene número de documento; no se puede buscar el PDF.")
      : t("detail_empty_not_found", "No se encontró un PDF que coincida con este registro.");
    $("#pdfFrameWrap").innerHTML = `<div class="pdf-empty">${escapeHtml(msg)}</div>`;
    $("#pdfHint").textContent = "";
  }

  function showPdf(relPath) {
    const cleanRel = relPath.startsWith("COMPRAS/") ? relPath : ("COMPRAS/" + relPath.replace(/^COMPRAS[\/\\]/, ""));
    const url = "/" + cleanRel.split("/").map(encodeURIComponent).join("/");
    $("#pdfFrameWrap").innerHTML = `<iframe src="${url}"></iframe>`;
    
    const fileTpl = t("detail_file_label", "Archivo: {path}");
    const fileText = fileTpl.replace("{path}", escapeHtml(relPath));
    const openText = t("detail_open_new_tab", "Abrir en pestaña nueva");
    $("#pdfHint").innerHTML = `${fileText} — <a href="${url}" target="_blank" rel="noopener">${escapeHtml(openText)}</a>`;
  }

  function wireEvents() {
    $("#btnBuscar").addEventListener("click", applyFilters);
    $("#qMed").addEventListener("keydown", (e) => { if (e.key === "Enter") applyFilters(); });
    ["fFechaDesde", "fFechaHasta", "fProveedor", "fEstado", "fDocumento", "fArchivo"].forEach((id) => {
      $("#" + id).addEventListener("change", applyFilters);
    });
    $("#fDocumento").addEventListener("keydown", (e) => { if (e.key === "Enter") applyFilters(); });
    $("#fArchivo").addEventListener("keydown", (e) => { if (e.key === "Enter") applyFilters(); });
    $("#btnLimpiar").addEventListener("click", () => { resetFiltersUI(); applyFilters(); });
    $("#btnSoloProblemas").addEventListener("click", () => {
      resetFiltersUI();
      extraFilter = { type: "cualquier_problema" };
      applyProblemFilter();
    });
    $("#btnPrev").addEventListener("click", () => { if (page > 0) { page--; renderTable(); } });
    $("#btnNext").addEventListener("click", () => { page++; renderTable(); });

    document.querySelectorAll("thead th[data-k]").forEach((th) => {
      th.addEventListener("click", () => {
        const k = th.dataset.k;
        if (sortKey === k) sortDir *= -1; else { sortKey = k; sortDir = 1; }
        sortFiltered();
        renderTable();
      });
    });
  }

  function applyProblemFilter() {
    const f = currentFilters();
    filtered = records.filter((r) => r.pdf_status !== "encontrado");
    sortFiltered();
    page = 0;
    renderFuzzy(f);
    renderTable();
  }

  load();
})();
