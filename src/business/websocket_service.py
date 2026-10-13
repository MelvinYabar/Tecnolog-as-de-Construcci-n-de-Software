# -*- coding: utf-8 -*-
"""
Servicio de Gestión y Difusión WebSocket (Business Layer).
Administra las conexiones en tiempo real de los auditores y la difusión
de eventos, alertas de sobrecosto y notas colaborativas.
"""
import json
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Set, Optional

logger = logging.getLogger(__name__)


class WebSocketBroadcasterService:
    """
    Servicio de lógica de negocio para WebSocket.
    Mantiene un registro concurrente (thread-safe) de clientes conectados
    y gestiona la difusión full-duplex de eventos en tiempo real.
    """

    def __init__(self):
        self._clients: Set[Any] = set()
        self._lock = threading.Lock()
        self._history = []
        self._max_history = 50

    @property
    def active_connections_count(self) -> int:
        with self._lock:
            return len(self._clients)

    def register_client(self, ws: Any) -> Dict[str, Any]:
        """Registra un nuevo cliente WebSocket y emite bienvenida."""
        with self._lock:
            self._clients.add(ws)
            count = len(self._clients)

        welcome_event = self._build_event(
            event_type="CONNECTION_ESTABLISHED",
            sender="Servidor Central de Auditoría GS",
            data={
                "message": "Conexión WebSocket establecida con éxito.",
                "active_auditors": count,
                "protocol": "RFC 6455 (Full-Duplex)",
                "channel": "/ws/audit"
            }
        )
        self._save_history(welcome_event)

        # Notificar actualización de presencia a todos los clientes
        presence_event = self._build_event(
            event_type="PRESENCE_UPDATE",
            sender="Monitor de Sesiones",
            data={
                "action": "AUDITOR_CONNECTED",
                "active_auditors": count,
                "message": f"Nuevo auditor conectado. Total en línea: {count}"
            }
        )
        self.broadcast_event(presence_event, exclude=ws)
        return welcome_event

    def unregister_client(self, ws: Any) -> None:
        """Remueve un cliente WebSocket y notifica la desconexión."""
        with self._lock:
            self._clients.discard(ws)
            count = len(self._clients)

        presence_event = self._build_event(
            event_type="PRESENCE_UPDATE",
            sender="Monitor de Sesiones",
            data={
                "action": "AUDITOR_DISCONNECTED",
                "active_auditors": count,
                "message": f"Auditor desconectado. Total en línea: {count}"
            }
        )
        self.broadcast_event(presence_event)

    def process_incoming_message(self, ws: Any, raw_message: str) -> Optional[Dict[str, Any]]:
        """
        Procesa un mensaje recibido desde el cliente, valida su estructura
        y retransmite el evento según corresponda.
        """
        try:
            payload = json.loads(raw_message)
        except Exception:
            return self._build_event(
                event_type="ERROR",
                sender="Sistema",
                data={"error": "Formato JSON inválido."}
            )

        msg_type = payload.get("type", "UNKNOWN")
        sender = payload.get("sender", "Auditor Anónimo")
        data = payload.get("data", {})

        if msg_type == "PING":
            return self._build_event(
                event_type="PONG",
                sender="Servidor WebSocket",
                data={"client_timestamp": data.get("timestamp"), "server_time": datetime.now().isoformat()}
            )

        elif msg_type == "PRICE_ALERT":
            # Alerta de sobrecosto o anomalía en precio de medicamento
            event = self._build_event(
                event_type="PRICE_ALERT",
                sender=sender,
                data={
                    "severity": "CRITICAL",
                    "invoice_number": data.get("invoice_number", "F001-00000000"),
                    "product": data.get("product", "Medicamento no especificado"),
                    "variance_pct": data.get("variance_pct", "+0%"),
                    "detail": data.get("detail", "Variación anormal detectada en costo unitario.")
                }
            )
            self._save_history(event)
            self.broadcast_event(event)
            return event

        elif msg_type == "AUDIT_NOTE":
            # Nota colaborativa sobre una factura en revisión
            event = self._build_event(
                event_type="AUDIT_NOTE",
                sender=sender,
                data={
                    "severity": "INFO",
                    "invoice_number": data.get("invoice_number", "N/A"),
                    "note": data.get("note", "Sin contenido"),
                    "status": data.get("status", "EN_REVISION")
                }
            )
            self._save_history(event)
            self.broadcast_event(event)
            return event

        else:
            event = self._build_event(
                event_type="GENERIC_MESSAGE",
                sender=sender,
                data=data
            )
            self._save_history(event)
            self.broadcast_event(event)
            return event

    def broadcast_event(self, event: Dict[str, Any], exclude: Optional[Any] = None) -> int:
        """
        Difunde un evento en formato JSON a todos los clientes conectados.
        Retorna la cantidad de clientes que recibieron el mensaje con éxito.
        """
        message_str = json.dumps(event, ensure_ascii=False)
        failed_clients = []
        sent_count = 0

        with self._lock:
            clients_snapshot = list(self._clients)

        for client in clients_snapshot:
            if client is exclude:
                continue
            try:
                client.send(message_str)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Error enviando mensaje WebSocket a cliente: {e}")
                failed_clients.append(client)

        if failed_clients:
            with self._lock:
                for fc in failed_clients:
                    self._clients.discard(fc)

        return sent_count

    def get_history(self) -> list:
        """Retorna el historial de los últimos eventos transmitidos."""
        with self._lock:
            return list(self._history)

    def _save_history(self, event: Dict[str, Any]) -> None:
        with self._lock:
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history.pop(0)

    def _build_event(self, event_type: str, sender: str, data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            count = len(self._clients)
        return {
            "type": event_type,
            "sender": sender,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "active_auditors": count,
            "data": data
        }
