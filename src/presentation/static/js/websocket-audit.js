/* Centro colaborativo de auditoría sobre WebSocket (RFC 6455). */
(() => {
  "use strict";

  const statusEl = document.getElementById("wsStatus");
  const audienceEl = document.getElementById("wsAudience");
  const latencyEl = document.getElementById("wsLatency");
  const feedEl = document.getElementById("wsFeed");
  const countEl = document.getElementById("wsEventCount");
  const formEl = document.getElementById("wsNoteForm");
  const sendButton = document.getElementById("wsSendNote");
  if (!statusEl || !formEl) return;

  let socket;
  let reconnectTimer;
  let pingTimer;
  let eventCount = 0;
  let reconnectAttempt = 0;

  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;").replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;").replaceAll('"', "&quot;");

  function setConnectionState(state, label) {
    statusEl.className = `ws-status ${state}`;
    statusEl.textContent = label;
    sendButton.disabled = state !== "online";
  }

  function updateAudience(count) {
    const total = Number(count) || 0;
    audienceEl.textContent = `${total} auditor${total === 1 ? "" : "es"} en línea`;
  }

  function addFeedItem(event) {
    if (feedEl.querySelector(".live-empty")) feedEl.innerHTML = "";
    eventCount += 1;
    countEl.textContent = `${eventCount} evento${eventCount === 1 ? "" : "s"}`;

    const data = event.data || {};
    const isAlert = event.type === "PRICE_ALERT";
    const isNote = event.type === "AUDIT_NOTE";
    const title = isAlert ? "Alerta de costo" : isNote ? "Nota colaborativa" : "Actualización de presencia";
    const body = isAlert
      ? `${data.product || "Producto"}: ${data.detail || "Variación detectada"}`
      : isNote ? data.note : data.message;
    const invoice = data.invoice_number && data.invoice_number !== "N/A"
      ? `<span class="live-invoice">${escapeHtml(data.invoice_number)}</span>` : "";

    const item = document.createElement("article");
    item.className = `live-event ${isAlert ? "critical" : isNote ? "note" : "presence"}`;
    item.innerHTML = `
      <div class="live-event-top"><strong>${escapeHtml(title)}</strong>${invoice}<time>${escapeHtml(event.timestamp || "Ahora")}</time></div>
      <p>${escapeHtml(body || "Evento recibido")}</p>
      <small>${escapeHtml(event.sender || "Servidor")}${data.status ? ` · ${escapeHtml(data.status.replaceAll("_", " "))}` : ""}</small>`;
    feedEl.prepend(item);
    while (feedEl.children.length > 8) feedEl.lastElementChild.remove();
  }

  function handleMessage(event) {
    let message;
    try { message = JSON.parse(event.data); } catch (_) { return; }
    updateAudience(message.active_auditors ?? message.data?.active_auditors);

    if (message.type === "CONNECTION_ESTABLISHED") {
      addFeedItem({ ...message, type: "PRESENCE_UPDATE" });
    } else if (message.type === "PONG") {
      const sentAt = Number(message.data?.client_timestamp);
      if (sentAt) latencyEl.textContent = `Latencia: ${Math.max(0, Date.now() - sentAt)} ms`;
    } else if (message.type !== "ERROR") {
      addFeedItem(message);
    } else {
      addFeedItem({ ...message, data: { message: message.data?.error } });
    }
  }

  function connect() {
    clearTimeout(reconnectTimer);
    setConnectionState("connecting", "Conectando…");
    const scheme = window.location.protocol === "https:" ? "wss" : "ws";
    socket = new WebSocket(`${scheme}://${window.location.host}/ws/audit`);

    socket.addEventListener("open", () => {
      reconnectAttempt = 0;
      setConnectionState("online", "En vivo");
      clearInterval(pingTimer);
      pingTimer = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: "PING", data: { timestamp: Date.now() } }));
        }
      }, 10000);
    });
    socket.addEventListener("message", handleMessage);
    socket.addEventListener("close", () => {
      clearInterval(pingTimer);
      setConnectionState("offline", "Reconectando…");
      updateAudience(0);
      reconnectAttempt += 1;
      reconnectTimer = setTimeout(connect, Math.min(1000 * (2 ** reconnectAttempt), 10000));
    });
    socket.addEventListener("error", () => socket.close());
  }

  formEl.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    const noteInput = document.getElementById("wsNote");
    socket.send(JSON.stringify({
      type: "AUDIT_NOTE",
      sender: "Auditor del dashboard",
      data: {
        invoice_number: document.getElementById("wsInvoice").value.trim(),
        note: noteInput.value.trim(),
        status: document.getElementById("wsNoteStatus").value,
      },
    }));
    noteInput.value = "";
    noteInput.focus();
  });

  window.addEventListener("beforeunload", () => {
    clearTimeout(reconnectTimer);
    clearInterval(pingTimer);
    if (socket) socket.close();
  });
  connect();
})();
