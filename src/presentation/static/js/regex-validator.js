/**
 * Regex Form Validator Controller (Presentation Layer).
 * Maneja la validación de campos mediante Expresiones Regulares en tiempo real (lado cliente)
 * y la sincronización con la Capa de Negocio (POST /api/invoices/validate-form).
 */
(function () {
  "use strict";

  // Diccionario de Expresiones Regulares compiladas (lado cliente)
  const REGEX_RULES = {
    invoice_number: {
      regex: /^[A-Z0-9]{1,5}-\d{4,8}$/,
      desc: "Serie (1-5 letras/números), guion y 4 a 8 dígitos (ej: F002-00012780)",
      error_es: "Debe cumplir formato: SERIE-NUMERO (ej: F002-00012780)",
      error_en: "Must match format: SERIES-NUMBER (e.g.: F002-00012780)",
      error_pt: "Deve seguir o formato: SERIE-NUMERO (ex: F002-00012780)"
    },
    ruc: {
      regex: /^(10|20)\d{9}$/,
      desc: "11 dígitos iniciando en 10 o 20 (ej: 20100123456)",
      error_es: "Debe tener exactamente 11 dígitos y comenzar con 10 o 20",
      error_en: "Must have exactly 11 digits starting with 10 or 20",
      error_pt: "Deve ter exatamente 11 dígitos começando com 10 ou 20"
    },
    sanitary_reg: {
      regex: /^[A-Z]{1,3}-\d{4,8}$/,
      desc: "Prefijo de 1-3 letras, guion y 4 a 8 dígitos (ej: EE-04821)",
      error_es: "Formato esperado: PREFIJO-NUMERO (ej: EE-04821)",
      error_en: "Expected format: PREFIX-NUMBER (e.g.: EE-04821)",
      error_pt: "Formato esperado: PREFIXO-NUMERO (ex: EE-04821)"
    },
    invoice_date: {
      regex: /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/,
      desc: "Formato ISO AAAA-MM-DD (ej: 2026-06-15)",
      error_es: "Fecha no válida. Debe ser AAAA-MM-DD (ej: 2026-06-15)",
      error_en: "Invalid date. Must be YYYY-MM-DD (e.g.: 2026-06-15)",
      error_pt: "Data inválida. Deve ser AAAA-MM-DD (ex: 2026-06-15)"
    },
    contact_email: {
      regex: /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/,
      desc: "Correo corporativo válido (ej: auditoria@farmacia.com)",
      error_es: "Correo no válido. Ingrese una dirección con @ y dominio",
      error_en: "Invalid email. Enter a valid address with @ and domain",
      error_pt: "E-mail inválido. Digite um endereço válido com @ e domínio"
    },
    total_amount: {
      regex: /^\d+(\.\d{1,4})?$/,
      desc: "Monto positivo con hasta 4 decimales (ej: 12450.75)",
      error_es: "Debe ser número positivo con hasta 4 decimales (ej: 1250.50)",
      error_en: "Must be a positive number with up to 4 decimals",
      error_pt: "Deve ser um número positivo com até 4 casas decimais"
    },
    pdf_filename: {
      regex: /^[\w\s.-]+\.(pdf|PDF)$/,
      desc: "Nombre de archivo finalizado en .pdf (ej: F002-00012780.pdf)",
      error_es: "El archivo debe terminar obligatoriamente en .pdf",
      error_en: "File name must strictly end with .pdf",
      error_pt: "O nome do arquivo deve terminar estritamente com .pdf"
    }
  };

  const SAMPLE_VALID = {
    invoice_number: "F002-00012780",
    ruc: "20100123456",
    sanitary_reg: "EE-04821",
    invoice_date: "2026-06-15",
    contact_email: "auditoria@castillo.com.pe",
    total_amount: "12450.75",
    pdf_filename: "F002-00012780 08.06.pdf"
  };

  const SAMPLE_INVALID = {
    invoice_number: "factura_sin_formato",
    ruc: "30999888",
    sanitary_reg: "REGISTRO-1234567890",
    invoice_date: "2026-15-40",
    contact_email: "correo_invalido_sin_arroba",
    total_amount: "-500.99999",
    pdf_filename: "factura_escaneada.docx"
  };

  const currentLang = window.CURRENT_LANG || "es";
  const I18N = window.I18N || {};

  function getErrorMessage(fieldName) {
    const rule = REGEX_RULES[fieldName];
    if (!rule) return "Campo inválido";
    return rule[`error_${currentLang}`] || rule.error_es;
  }

  function validateSingleField(fieldName) {
    const input = document.getElementById("rx_" + fieldName);
    const badge = document.getElementById("badge_" + fieldName);
    const errSpan = document.getElementById("err_" + fieldName);
    if (!input || !REGEX_RULES[fieldName]) return true;

    const val = input.value.trim();
    const rule = REGEX_RULES[fieldName];

    if (!val) {
      input.style.borderColor = "#2a3b4a";
      if (badge) badge.style.display = "none";
      if (errSpan) errSpan.textContent = "";
      return false;
    }

    const isValid = rule.regex.test(val);

    if (isValid) {
      input.style.borderColor = "#34c88a";
      if (badge) {
        badge.style.display = "inline-block";
        badge.className = "badge ok";
        badge.textContent = currentLang === "en" ? "✔ Valid" : "✔ Válido";
      }
      if (errSpan) errSpan.textContent = "";
    } else {
      input.style.borderColor = "#f0616d";
      if (badge) {
        badge.style.display = "inline-block";
        badge.className = "badge bad";
        badge.textContent = currentLang === "en" ? "✖ Invalid" : "✖ Inválido";
      }
      if (errSpan) errSpan.textContent = getErrorMessage(fieldName);
    }

    return isValid;
  }

  function validateAllFields() {
    let allValid = true;
    for (const fieldName of Object.keys(REGEX_RULES)) {
      const isFieldValid = validateSingleField(fieldName);
      if (!isFieldValid) allValid = false;
    }
    return allValid;
  }

  function getFormData() {
    const data = {};
    for (const fieldName of Object.keys(REGEX_RULES)) {
      const input = document.getElementById("rx_" + fieldName);
      data[fieldName] = input ? input.value.trim() : "";
    }
    return data;
  }

  function setFormData(data) {
    for (const [key, val] of Object.entries(data)) {
      const input = document.getElementById("rx_" + key);
      if (input) {
        input.value = val;
        validateSingleField(key);
      }
    }
  }

  function clearForm() {
    for (const fieldName of Object.keys(REGEX_RULES)) {
      const input = document.getElementById("rx_" + fieldName);
      const badge = document.getElementById("badge_" + fieldName);
      const errSpan = document.getElementById("err_" + fieldName);
      if (input) {
        input.value = "";
        input.style.borderColor = "#2a3b4a";
      }
      if (badge) badge.style.display = "none";
      if (errSpan) errSpan.textContent = "";
    }
    const alertBox = document.getElementById("regexAlertBox");
    if (alertBox) alertBox.style.display = "none";
    const outBox = document.getElementById("regexServerOutput");
    if (outBox) outBox.style.display = "none";
  }

  function showAlert(message, isSuccess) {
    const alertBox = document.getElementById("regexAlertBox");
    if (!alertBox) return;
    alertBox.style.display = "block";
    if (isSuccess) {
      alertBox.style.background = "rgba(52, 200, 138, 0.15)";
      alertBox.style.border = "1px solid #34c88a";
      alertBox.style.color = "#34c88a";
      alertBox.innerHTML = "✅ " + message;
    } else {
      alertBox.style.background = "rgba(240, 97, 109, 0.15)";
      alertBox.style.border = "1px solid #f0616d";
      alertBox.style.color = "#f0616d";
      alertBox.innerHTML = "⚠️ " + message;
    }
  }

  async function submitToServer() {
    const data = getFormData();
    const isClientValid = validateAllFields();

    const submitBtn = document.getElementById("btnSubmitRegex");
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = currentLang === "en" ? "Validating on Server..." : "Validando en Servidor...";
    }

    try {
      const res = await fetch("/api/invoices/validate-form", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      const json = await res.json();

      const outBox = document.getElementById("regexServerOutput");
      const pre = document.getElementById("regexJsonPre");
      const badge = document.getElementById("serverStatusBadge");

      if (outBox && pre) {
        outBox.style.display = "block";
        pre.textContent = JSON.stringify(json, null, 2);
        if (json.is_valid) {
          pre.style.color = "#34c88a";
          if (badge) {
            badge.style.color = "#34c88a";
            badge.textContent = "✔ HTTP 200 OK — TODAS LAS REGLAS REGEX CUMPLIDAS";
          }
          const successMsg = I18N.regex_success_alert || "¡Formulario validado con éxito! Todos los campos cumplen con las Expresiones Regulares.";
          showAlert(successMsg, true);
        } else {
          pre.style.color = "#f0616d";
          if (badge) {
            badge.style.color = "#f0616d";
            badge.textContent = `✖ HTTP 200 OK — ${Object.keys(json.errors || {}).length} ERRORES DE REGEX DETECTADOS`;
          }
          const errMsg = I18N.regex_error_alert || "Se encontraron errores de validación. Por favor corrija los campos señalados en rojo.";
          showAlert(errMsg, false);
        }
      }
    } catch (err) {
      showAlert("Error de conexión al validar con la capa de negocio: " + err.message, false);
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = I18N.regex_btn_validate ? ("🚀 " + I18N.regex_btn_validate) : "🚀 Validar en Servidor (Capa de Negocio)";
      }
    }
  }

  // Inicialización de Event Listeners
  document.addEventListener("DOMContentLoaded", function () {
    for (const fieldName of Object.keys(REGEX_RULES)) {
      const input = document.getElementById("rx_" + fieldName);
      if (input) {
        input.addEventListener("input", () => validateSingleField(fieldName));
        input.addEventListener("blur", () => validateSingleField(fieldName));
      }
    }

    const btnFillValid = document.getElementById("btnFillValid");
    if (btnFillValid) {
      btnFillValid.addEventListener("click", () => {
        setFormData(SAMPLE_VALID);
        const successMsg = currentLang === "en" 
          ? "Valid sample loaded. All fields match their Regular Expressions!"
          : "Ejemplo válido cargado. ¡Todos los campos cumplen con sus Expresiones Regulares!";
        showAlert(successMsg, true);
      });
    }

    const btnFillInvalid = document.getElementById("btnFillInvalid");
    if (btnFillInvalid) {
      btnFillInvalid.addEventListener("click", () => {
        setFormData(SAMPLE_INVALID);
        const errMsg = currentLang === "en"
          ? "Erroneous sample loaded. Regular Expressions detected invalid formats."
          : "Ejemplo con errores cargado. Las Expresiones Regulares detectaron formatos inválidos.";
        showAlert(errMsg, false);
      });
    }

    const btnClear = document.getElementById("btnClearRegex");
    if (btnClear) {
      btnClear.addEventListener("click", clearForm);
    }

    const btnSubmit = document.getElementById("btnSubmitRegex");
    if (btnSubmit) {
      btnSubmit.addEventListener("click", submitToServer);
    }

    // Auto-disparador opcional para pruebas y capturas automatizadas
    const urlParams = new URLSearchParams(window.location.search);
    const demoMode = urlParams.get("demo_regex");
    if (demoMode === "valid") {
      setTimeout(() => {
        if (btnFillValid) btnFillValid.click();
        setTimeout(() => { if (btnSubmit) btnSubmit.click(); }, 300);
      }, 300);
    } else if (demoMode === "invalid") {
      setTimeout(() => {
        if (btnFillInvalid) btnFillInvalid.click();
        setTimeout(() => { if (btnSubmit) btnSubmit.click(); }, 300);
      }, 300);
    }
  });
})();
