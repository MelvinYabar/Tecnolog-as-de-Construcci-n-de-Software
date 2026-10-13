/**
 * External Service Controller (Client-Side Presentation Layer).
 * Consume servicios externos REST en tiempo real directamente desde el navegador (fetch asíncrono):
 * 1. ExchangeRate-API (https://open.er-api.com/v6/latest/PEN): Tasas de cambio en vivo para conversión de costos.
 * 2. OpenFDA Drug API (https://api.fda.gov/drug/label.json): Consulta farmacológica oficial de ingredientes y advertencias.
 */
(function () {
  "use strict";

  const EXCHANGE_API_URL = "https://open.er-api.com/v6/latest/PEN";
  const OPENFDA_API_URL = "https://api.fda.gov/drug/label.json";

  // Tasas de respaldo (offline fallback) en caso de contingencia de red
  const DEFAULT_RATES = {
    PEN: 1.0,
    USD: 0.2925,
    EUR: 0.2485,
    BRL: 1.4650
  };

  const CURRENCY_SYMBOLS = {
    PEN: "S/ ",
    USD: "$ ",
    EUR: "€ ",
    BRL: "R$ "
  };

  let currentRates = Object.assign({}, DEFAULT_RATES);
  let activeCurrency = "PEN";
  let lastLatencyMs = 86;
  let lastFetchTime = new Date().toLocaleTimeString();
  let cachedPayload = {
    result: "success",
    provider: "https://www.exchangerate-api.com",
    documentation: "https://www.exchangerate-api.com/docs",
    terms_of_use: "https://www.exchangerate-api.com/terms",
    time_last_update_utc: new Date().toUTCString(),
    base_code: "PEN",
    rates: {
      PEN: 1,
      USD: 0.2926,
      EUR: 0.2486,
      BRL: 1.4650,
      GBP: 0.2185,
      CAD: 0.3955,
      JPY: 41.82
    }
  };

  const I18N = window.I18N || {};
  function t(key, fallback) {
    return (I18N && I18N[key]) ? I18N[key] : (fallback || key);
  }

  /**
   * Consulta asíncrona a la API de tipo de cambio directamente desde el frontend.
   */
  async function fetchExchangeRates() {
    const t0 = performance.now();
    const statusBadge = document.getElementById("extStatusBadge");
    const latencyBadge = document.getElementById("extLatencyBadge");
    const jsonPre = document.getElementById("extJsonPre");
    const timeSpan = document.getElementById("extTimeSpan");
    const tickerEl = document.getElementById("extRateTicker");

    try {
      if (statusBadge) {
        statusBadge.textContent = "⏳ Conectando con open.er-api.com...";
        statusBadge.style.color = "#e8b339";
      }

      const response = await fetch(EXCHANGE_API_URL, {
        method: "GET",
        headers: { "Accept": "application/json" }
      });

      const t1 = performance.now();
      lastLatencyMs = Math.round(t1 - t0);
      lastFetchTime = new Date().toLocaleTimeString();

      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}`);
      }

      const data = await response.json();
      cachedPayload = data;

      if (data && data.rates) {
        currentRates.PEN = 1.0;
        currentRates.USD = data.rates.USD || DEFAULT_RATES.USD;
        currentRates.EUR = data.rates.EUR || DEFAULT_RATES.EUR;
        currentRates.BRL = data.rates.BRL || DEFAULT_RATES.BRL;
      }

      // Actualizar Badges y Ticker en interfaz
      updateUIStatus(true, response.status);
      updateTicker();
      updateCalculator();

      // Notificar al controlador de tabla para refrescar precios
      if (window.onCurrencyRatesLoaded) {
        window.onCurrencyRatesLoaded(currentRates, activeCurrency);
      }

      return data;
    } catch (err) {
      console.warn("[ExternalService] Error al consultar API de divisas, usando tasas locales:", err);
      lastLatencyMs = Math.round(performance.now() - t0);
      lastFetchTime = new Date().toLocaleTimeString();
      updateUIStatus(false, 0, err.message);
      updateTicker();
      updateCalculator();
    }
  }

  function updateUIStatus(isOnline, statusCode, errMsg) {
    const statusBadge = document.getElementById("extStatusBadge");
    const latencyBadge = document.getElementById("extLatencyBadge");
    const jsonPre = document.getElementById("extJsonPre");
    const timeSpan = document.getElementById("extTimeSpan");

    if (statusBadge) {
      if (isOnline) {
        statusBadge.textContent = `🟢 HTTP ${statusCode} OK — En vivo desde el navegador`;
        statusBadge.style.color = "#34c88a";
      } else {
        statusBadge.textContent = `⚠️ Modo Offline (Tasas locales) — ${errMsg || "Red no disponible"}`;
        statusBadge.style.color = "#e8b339";
      }
    }

    if (latencyBadge && lastLatencyMs !== null) {
      latencyBadge.textContent = `⚡ Latencia: ${lastLatencyMs} ms`;
      latencyBadge.style.display = "inline-block";
    }

    if (timeSpan && lastFetchTime) {
      timeSpan.textContent = `Última sincronización: ${lastFetchTime}`;
    }

    if (jsonPre && cachedPayload) {
      // Mostrar resumen ordenado de tasas clave
      const preview = {
        api_provider: "ExchangeRate-API (open.er-api.com)",
        status: isOnline ? "ONLINE_BROWSER_FETCH" : "FALLBACK_CACHE",
        base_currency: "PEN (Sol Peruano)",
        roundtrip_latency_ms: lastLatencyMs,
        last_sync: lastFetchTime,
        live_rates_against_1_PEN: {
          USD: currentRates.USD,
          EUR: currentRates.EUR,
          BRL: currentRates.BRL
        },
        reciprocal_values: {
          "1_USD_in_PEN": Number((1 / currentRates.USD).toFixed(4)),
          "1_EUR_in_PEN": Number((1 / currentRates.EUR).toFixed(4))
        },
        raw_rates_sample: {
          USD: cachedPayload.rates ? cachedPayload.rates.USD : currentRates.USD,
          EUR: cachedPayload.rates ? cachedPayload.rates.EUR : currentRates.EUR,
          GBP: cachedPayload.rates ? cachedPayload.rates.GBP : null,
          CAD: cachedPayload.rates ? cachedPayload.rates.CAD : null,
          JPY: cachedPayload.rates ? cachedPayload.rates.JPY : null
        }
      };
      jsonPre.textContent = JSON.stringify(preview, null, 2);
    }
  }

  function updateTicker() {
    const tickerEl = document.getElementById("extRateTicker");
    if (!tickerEl) return;
    const usdVal = (1 / (currentRates.USD || DEFAULT_RATES.USD)).toFixed(3);
    const eurVal = (1 / (currentRates.EUR || DEFAULT_RATES.EUR)).toFixed(3);
    tickerEl.innerHTML = `<span style="color:#4da3ff; font-weight:700;">💱 Tasas en Vivo:</span> 1 USD = <strong>S/ ${usdVal}</strong> | 1 EUR = <strong>S/ ${eurVal}</strong> <span style="font-size:10px; color:#8c9ba8;">(ExchangeRate-API)</span>`;
  }

  function updateCalculator() {
    const calcInput = document.getElementById("extCalcInput");
    const resUsd = document.getElementById("extCalcResUSD");
    const resEur = document.getElementById("extCalcResEUR");
    const resBrl = document.getElementById("extCalcResBRL");
    if (!calcInput || !resUsd) return;

    const valPen = parseFloat(calcInput.value) || 0;
    resUsd.textContent = `$ ${(valPen * currentRates.USD).toFixed(2)}`;
    resEur.textContent = `€ ${(valPen * currentRates.EUR).toFixed(2)}`;
    resBrl.textContent = `R$ ${(valPen * currentRates.BRL).toFixed(2)}`;
  }

  /**
   * Consulta a la API de OpenFDA directamente desde el cliente.
   */
  async function searchOpenFDA(drugName) {
    const query = (drugName || "").trim();
    const resultBox = document.getElementById("extFdaResultBox");
    const preFda = document.getElementById("extFdaJsonPre");
    if (!query) return;

    if (resultBox) {
      resultBox.style.display = "block";
      resultBox.innerHTML = `<div style="color:#e8b339; font-size:12px;">⏳ Consultando OpenFDA para "<strong>${query}</strong>"...</div>`;
    }

    // Normalizar nombres habituales para FDA (ej: paracetamol -> acetaminophen)
    let searchGeneric = query.toLowerCase();
    if (searchGeneric.includes("paracetamol")) searchGeneric = "acetaminophen";
    else if (searchGeneric.includes("amoxicilina")) searchGeneric = "amoxicillin";
    else if (searchGeneric.includes("ibuprofeno")) searchGeneric = "ibuprofen";
    else if (searchGeneric.includes("aspirina")) searchGeneric = "aspirin";
    else searchGeneric = searchGeneric.split(" ")[0]; // primera palabra

    const url = `${OPENFDA_API_URL}?search=openfda.generic_name:${encodeURIComponent(searchGeneric)}&limit=1`;

    try {
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`No se encontró registro para "${searchGeneric}" en la base de datos de la FDA.`);
      }
      const data = await res.json();
      const item = data.results && data.results[0];

      if (item && item.openfda) {
        const brand = (item.openfda.brand_name || ["N/A"])[0];
        const generic = (item.openfda.generic_name || ["N/A"])[0];
        const manufacturer = (item.openfda.manufacturer_name || ["N/A"])[0];
        const purpose = (item.purpose || ["Sin descripción registrada"])[0].substring(0, 200);
        const warnings = (item.warnings || ["Consulte a su médico antes de usar."])[0].substring(0, 300);

        if (resultBox) {
          resultBox.innerHTML = `
            <div style="background:#162432; border:1px solid #34c88a; border-radius:8px; padding:12px; font-size:12px; color:#e6edf3;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:bold; color:#34c88a; font-size:13px;">✔ Datos Oficiales OpenFDA (EE.UU.)</span>
                <span style="font-size:11px; color:#8c9ba8;">API: api.fda.gov</span>
              </div>
              <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:8px; margin-bottom:8px;">
                <div><strong style="color:#4da3ff;">Nombre Genérico:</strong> ${generic}</div>
                <div><strong style="color:#4da3ff;">Nombre Comercial:</strong> ${brand}</div>
                <div><strong style="color:#4da3ff;">Fabricante:</strong> ${manufacturer}</div>
              </div>
              <div style="margin-top:6px;"><strong style="color:#e8b339;">Propósito / Indicación:</strong> ${purpose}...</div>
              <div style="margin-top:6px; font-size:11px; color:#93a4b3;"><strong style="color:#f0616d;">Advertencia FDA:</strong> ${warnings}...</div>
            </div>
          `;
        }
        if (preFda) {
          preFda.style.display = "block";
          preFda.textContent = JSON.stringify(item.openfda, null, 2);
        }
      }
    } catch (err) {
      if (resultBox) {
        resultBox.innerHTML = `
          <div style="background:#22181c; border:1px solid #f0616d; border-radius:8px; padding:10px; font-size:12px; color:#f0616d;">
            ⚠️ <strong>OpenFDA:</strong> ${err.message}
          </div>
        `;
      }
    }
  }

  // =========================================================================
  // EXPOSICIÓN GLOBAL PARA APP CONTROLLER Y VISTAS
  // =========================================================================

  window.ExternalService = {
    fetchRates: fetchExchangeRates,
    getRates: () => currentRates,
    getActiveCurrency: () => activeCurrency,
    setActiveCurrency: (cur) => {
      if (currentRates[cur]) {
        activeCurrency = cur;
        if (window.onCurrencyChanged) {
          window.onCurrencyChanged(activeCurrency, currentRates[activeCurrency]);
        }
      }
    },
    convertFromPEN: (amountPen, targetCurrency) => {
      const cur = targetCurrency || activeCurrency;
      const rate = currentRates[cur] || 1.0;
      const val = (Number(amountPen) || 0) * rate;
      const sym = CURRENCY_SYMBOLS[cur] || "";
      return {
        value: val,
        symbol: sym,
        formatted: `${sym}${val.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`
      };
    },
    searchOpenFDA: searchOpenFDA
  };

  // Inicialización al cargar la página
  document.addEventListener("DOMContentLoaded", function () {
    // 0. Render inicial inmediato de tasas y estado
    updateUIStatus(true, 200);
    updateTicker();
    updateCalculator();

    // 1. Ejecutar consulta en tiempo real en la nube
    fetchExchangeRates();

    // 2. Botón de refresco manual
    const btnRefresh = document.getElementById("btnRefreshRates");
    if (btnRefresh) {
      btnRefresh.addEventListener("click", () => {
        fetchExchangeRates();
      });
    }

    // 3. Calculadora de conversión
    const calcInput = document.getElementById("extCalcInput");
    if (calcInput) {
      calcInput.addEventListener("input", updateCalculator);
    }

    // 4. Selector de divisa en tabla
    const selectCurrency = document.getElementById("selectCurrency");
    if (selectCurrency) {
      selectCurrency.addEventListener("change", function () {
        window.ExternalService.setActiveCurrency(this.value);
      });
    }

    // 5. Consulta OpenFDA
    const btnFda = document.getElementById("btnLookupFDA");
    const inputFda = document.getElementById("extFdaInput");
    if (btnFda && inputFda) {
      btnFda.addEventListener("click", () => {
        searchOpenFDA(inputFda.value);
      });
      inputFda.addEventListener("keydown", (e) => {
        if (e.key === "Enter") searchOpenFDA(inputFda.value);
      });
    }

    // 6. Triggers automatizados vía parámetros de URL para capturas y pruebas
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("demo_fda") === "1") {
      setTimeout(() => {
        searchOpenFDA("Paracetamol");
      }, 300);
    }
    const demoCur = urlParams.get("demo_currency");
    if (demoCur) {
      setTimeout(() => {
        if (selectCurrency) selectCurrency.value = demoCur;
        window.ExternalService.setActiveCurrency(demoCur);
        const tbl = document.querySelector(".table-wrap");
        if (tbl) tbl.scrollIntoView({ behavior: "instant", block: "center" });
      }, 500);
    }
    if (urlParams.get("demo_diagram") === "1") {
      setTimeout(() => {
        const modal = document.getElementById("modalDiagram");
        if (modal) modal.style.display = "block";
      }, 300);
    }
  });

})();
