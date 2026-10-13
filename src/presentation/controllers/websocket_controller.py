# -*- coding: utf-8 -*-
"""Adaptador WebSocket de la capa de presentación."""
import json

from flask import current_app, session


def register_websocket_routes(sock) -> None:
    """Registra el canal de colaboración en tiempo real del dashboard."""

    @sock.route("/ws/audit")
    def audit_socket(ws):
        service = current_app.websocket_service

        if not session.get("logged_in"):
            ws.send(json.dumps({
                "type": "ERROR",
                "sender": "Sistema",
                "data": {"error": "Sesión no autenticada."},
            }, ensure_ascii=False))
            ws.close()
            return

        welcome = service.register_client(ws)
        ws.send(json.dumps(welcome, ensure_ascii=False))

        try:
            while True:
                raw_message = ws.receive()
                if raw_message is None:
                    break
                response = service.process_incoming_message(ws, raw_message)
                # Los eventos colaborativos ya fueron difundidos por el servicio.
                # PONG y ERROR son respuestas privadas para el cliente que los originó.
                if response and response.get("type") in {"PONG", "ERROR"}:
                    ws.send(json.dumps(response, ensure_ascii=False))
        finally:
            service.unregister_client(ws)
