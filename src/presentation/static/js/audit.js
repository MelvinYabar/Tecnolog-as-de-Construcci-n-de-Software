(function () {
  "use strict";

  const PAGE_SIZE = 60;
  const $ = (sel) => document.querySelector(sel);

  let DATA = null;
  let items = [];
  let filtered = [];
  let page = 0;
  let sortKey = null;
  let sortDir = 1;
  let selectedRow = null;

  function stripAccents(s) {
    return (s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }
  function normText(s) {
    return stripAccents(String(s || "")).toLowerCase().trim();
  }
  function fmtMoney(n) {
    if (n === null || n === undefined || n === "") return "-";
    const v = Number(n);
    if (Number.isNaN(v)) return String(n);
    return "S/ " + v.toLocaleString("es-PE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function fmtPct(n) {
    if (n === null || n === undefined) return "-";
    return (n * 100).toFixed(0) + "%";
  }
  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  function estadoInfo(p) {
    const parts = [];
    let cls = "ok";
    if (p.sin_factura) { parts.push("Sin factura de respaldo"); cls = "bad"; }
    if (p.precio_topado) { parts.push("Precio sugerido topado"); cls = "warn"; }
    if (p.margen_atipico) { parts.push("Margen atípico - revisar match"); cls = "warn"; }
    if (!p.ikf_precio) { parts.push("IKF: revisión manual"); if (cls === "ok") cls = "warn"; }
    if (p.match_score !== null && p.match_score !== undefined && p.match_score < 0.22 && !p.sin_factura) {
      parts.push("Coincidencia de nombre a revisar");
      if (cls === "ok") cls = "warn";
    }
    if (!parts.length) { parts.push("OK"); }
    return { text: parts.join(" | "), cls };
  }

  async function load() {
    let res;
    try {
      res = await fetch("/api/audit/data", { cache: "no-store" });
      if (!res.ok) {
        res = await fetch("audit_data.json", { cache: "no-store" });
      }
    } catch (e) {
      res = await fetch("audit_data.json", { cache: "no-store" });
    }

    if (!res || !res.ok) return;
    DATA = await res.json();
    items = (DATA.productos || []).map((p) => {
      const est = estadoInfo(p);
      return Object.assign({}, p, { estado_txt: est.text, estado_cls: est.cls });
    });
    fillProveedorOptions();
    renderCards();
    applyFilters();
    wireEvents();
    wireTabs();
  }

  function fillProveedorOptions() {
    const sel = $("#aProveedor");
    const provs = new Set();
    items.forEach((p) => {
      if (p.proveedor) String(p.proveedor).split(",").forEach((x) => provs.add(x.trim()));
    });
    [...provs].sort().forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p; opt.textContent = p;
      sel.appendChild(opt);
    });
  }

  function renderCards() {
    const total = items.length;
    const sinFactura = items.filter((p) => p.sin_factura).length;
    const conIkf = items.filter((p) => p.ikf_precio).length;
    const topados = items.filter((p) => p.precio_topado).length;
    const margenNeg = items.filter((p) => p.margen_pct !== null && p.margen_pct !== undefined && p.margen_pct < 0).length;
    const cards = [
      { num: total, lbl: "SKUs auditados" },
      { num: total - sinFactura, lbl: "Con factura de respaldo", cls: "ok" },
      { num: sinFactura, lbl: "Sin factura de respaldo", cls: "bad" },
      { num: conIkf, lbl: "Con precio Inkafarma", cls: "ok" },
      { num: total - conIkf, lbl: "IKF pendiente (revisión manual)", cls: "warn" },
      { num: topados, lbl: "Precio sugerido topado", cls: "warn" },
      { num: margenNeg, lbl: "Margen real negativo (vs IKF)", cls: "bad" },
    ];
    $("#auditCards").innerHTML = cards
      .map((c) => `<div class="card ${c.cls || ""}"><div class="num">${c.num}</div><div class="lbl">${c.lbl}</div></div>`)
      .join("");
  }

  function currentFilters() {
    return {
      q: normText($("#aqMed").value),
      proveedor: $("#aProveedor").value,
      estado: $("#aEstado").value,
      margen: $("#aMargen").value,
    };
  }

  function matches(p, f) {
    if (f.proveedor && !(p.proveedor || "").includes(f.proveedor)) return false;
    if (f.q) {
      const hay = normText((p.nombre || "") + " " + (p.presentacion || "") + " " + (p.principio_activo || ""));
      if (!hay.includes(f.q)) return false;
    }
    if (f.estado === "sin_factura" && !p.sin_factura) return false;
    if (f.estado === "topado" && !p.precio_topado) return false;
    if (f.estado === "sin_ikf" && p.ikf_precio) return false;
    if (f.estado === "revisar_match" && !(p.match_score !== null && p.match_score !== undefined && p.match_score < 0.22 && !p.sin_factura)) return false;
    if (f.margen) {
      const m = p.margen_pct;
      if (f.margen === "na" && m !== null && m !== undefined) return false;
      if (f.margen === "neg" && !(m !== null && m !== undefined && m < 0)) return false;
      if (f.margen === "low" && !(m !== null && m !== undefined && m >= 0 && m <= 0.15)) return false;
      if (f.margen === "ok" && !(m !== null && m !== undefined && m > 0.15)) return false;
    }
    return true;
  }

  function applyFilters() {
    const f = currentFilters();
    filtered = items.filter((p) => matches(p, f));
    sortFiltered();
    page = 0;
    renderTable();
  }

  function sortFiltered() {
    if (!sortKey) return;
    filtered.sort((a, b) => {
      let av = a[sortKey], bv = b[sortKey];
      if (av === null || av === undefined) av = "";
      if (bv === null || bv === undefined) bv = "";
      if (typeof av === "number" || typeof bv === "number") { av = Number(av) || 0; bv = Number(bv) || 0; }
      if (av < bv) return -1 * sortDir;
      if (av > bv) return 1 * sortDir;
      return 0;
    });
  }

  function renderTable() {
    const total = filtered.length;
    const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    if (page >= totalPages) page = totalPages - 1;
    const start = page * PAGE_SIZE;
    const pageItems = filtered.slice(start, start + PAGE_SIZE);

    $("#auditResultMeta").textContent = `${total} producto(s) encontrado(s)`;

    $("#auditTbody").innerHTML = pageItems.map((p) => {
      const cls = p.row_idx === selectedRow ? "selected" : "";
      const margenCls = p.margen_pct === null || p.margen_pct === undefined ? "" : p.margen_pct < 0 ? "bad" : p.margen_pct <= 0.15 ? "warn" : "ok";
      return `<tr class="${cls}" data-row="${p.row_idx}">
        <td title="${escapeHtml(p.nombre)}">${escapeHtml(p.nombre)}</td>
        <td title="${escapeHtml(p.presentacion)}">${escapeHtml(p.presentacion)}</td>
        <td title="${escapeHtml(p.concentracion || "")}">${escapeHtml(p.concentracion || "-")}</td>
        <td title="${escapeHtml(p.principio_activo || "")}">${escapeHtml(p.principio_activo || "-")}</td>
        <td>${escapeHtml(p.registro_sanitario || "-")}</td>
        <td>${fmtMoney(p.costo_lista)}</td>
        <td>${fmtMoney(p.costo_descuento)}</td>
        <td title="${escapeHtml(p.proveedor || "")}">${escapeHtml(p.proveedor || "-")}</td>
        <td>${fmtMoney(p.precio_recalculado)}</td>
        <td>${fmtMoney(p.ikf_precio)}${p.ikf_precio_unitario !== p.ikf_precio && p.ikf_cantidad_envase ? ` <span class="hint">(÷${p.ikf_cantidad_envase})</span>` : ""}</td>
        <td>${fmtMoney(p.ikf_precio_unitario)}</td>
        <td><span class="badge ${margenCls}" title="${p.margen_atipico ? 'Atípico: posible match de dosis/presentación incorrecto, revisar' : ''}">${fmtPct(p.margen_pct)}${p.margen_atipico ? " ⚠" : ""}</span></td>
        <td><a class="ikf-link" href="${p.ikf_link}" target="_blank" rel="noopener" onclick="event.stopPropagation()">Ver en Inkafarma ↗</a></td>
        <td><span class="badge ${p.estado_cls}">${escapeHtml(p.estado_txt)}</span></td>
      </tr>`;
    }).join("");

    $("#auditTbody").querySelectorAll("tr").forEach((tr) => {
      tr.addEventListener("click", () => selectRow(Number(tr.dataset.row)));
    });

    $("#auditPagerInfo").textContent = `Página ${page + 1} de ${totalPages}`;
    $("#aBtnPrev").disabled = page <= 0;
    $("#aBtnNext").disabled = page >= totalPages - 1;
  }

  function selectRow(rowIdx) {
    selectedRow = rowIdx;
    const p = items.find((x) => x.row_idx === rowIdx);
    if (!p) return;
    renderTable();
    $("#auditDetailPanel").style.display = "";
    const kv = [
      ["Producto", p.nombre],
      ["Presentación", p.presentacion],
      ["Concentración", p.concentracion || "-"],
      ["Principio Activo", p.principio_activo || "-"],
      ["Registro Sanitario", p.registro_sanitario || "-"],
      ["Costo Lista (crudo, sin desc., con IGV)", fmtMoney(p.costo_lista) + (p.costo_lista_original != null && Math.abs((p.costo_lista_original||0) - (p.costo_lista||0)) > 0.01 ? ` (original: ${fmtMoney(p.costo_lista_original)})` : "")],
      ["Mediana de mercado", fmtMoney(p.mediana)],
      ["Costo con Descuento (neto real)", fmtMoney(p.costo_descuento)],
      ["Proveedor", p.proveedor || "-"],
      ["N° Factura", p.n_factura || "-"],
      ["Fecha última factura", p.fecha_factura || "-"],
      ["% Descuento/Variación de costo", p.descuento_pct != null ? (p.descuento_pct * 100).toFixed(0) + "%" : "-"],
      ["Volumen prom./mes (proxy compras)", p.volumen_prom_mes ?? "-"],
      ["Frecuencia de compras (proxy)", p.frecuencia_compras ?? "-"],
      ["Precio Recalculado (30% margen)", fmtMoney(p.precio_recalculado)],
      ["Precio Inkafarma - caja/envase completo", p.ikf_precio ? fmtMoney(p.ikf_precio) + (p.ikf_cantidad_envase ? ` (x${p.ikf_cantidad_envase})` : "") + " — " + escapeHtml(p.ikf_producto || "") : "Revisión manual"],
      ["Precio Inkafarma - POR UNIDAD", fmtMoney(p.ikf_precio_unitario)],
      ["Margen real (vs IKF unitario o mediana)", fmtPct(p.margen_pct) + (p.margen_fuente ? ` (ref: ${p.margen_fuente})` : "")],
      ["Link de búsqueda en Inkafarma", `<a class="ikf-link" href="${p.ikf_link}" target="_blank" rel="noopener">${p.ikf_link}</a>`],
      ["Precio tope sugerido", p.tope_sugerido ? fmtMoney(p.tope_sugerido) : "-"],
      ["Estado", `<span class="badge ${p.estado_cls}">${escapeHtml(p.estado_txt)}</span>`],
      ["Nota / ambigüedad", p.ambiguous_note || p.no_cost_match || "-"],
    ];
    $("#auditDetailKv").innerHTML = kv
      .map(([k, v]) => `<div class="k">${escapeHtml(k)}</div><div class="v">${typeof v === "string" && v.includes("<") ? v : escapeHtml(v)}</div>`)
      .join("");
  }

  function resetFiltersUI() {
    $("#aqMed").value = "";
    $("#aProveedor").value = "";
    $("#aEstado").value = "";
    $("#aMargen").value = "";
  }

  function wireEvents() {
    $("#aBtnBuscar").addEventListener("click", applyFilters);
    $("#aqMed").addEventListener("keydown", (e) => { if (e.key === "Enter") applyFilters(); });
    ["aProveedor", "aEstado", "aMargen"].forEach((id) => $("#" + id).addEventListener("change", applyFilters));
    $("#aBtnLimpiar").addEventListener("click", () => { resetFiltersUI(); applyFilters(); });
    $("#aBtnPrev").addEventListener("click", () => { if (page > 0) { page--; renderTable(); } });
    $("#aBtnNext").addEventListener("click", () => { page++; renderTable(); });
    document.querySelectorAll("#tabAuditoria thead th[data-k]").forEach((th) => {
      th.addEventListener("click", () => {
        const k = th.dataset.k;
        if (sortKey === k) sortDir *= -1; else { sortKey = k; sortDir = 1; }
        sortFiltered();
        renderTable();
      });
    });
  }

  function wireTabs() {
    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".tabpanel").forEach((p) => (p.style.display = "none"));
        btn.classList.add("active");
        document.getElementById(btn.dataset.tab).style.display = "";
      });
    });
  }

  load();
})();
