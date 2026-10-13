# -*- coding: utf-8 -*-
"""Pruebas unitarias del servicio de difusión WebSocket."""
import json
import unittest

from src.business.websocket_service import WebSocketBroadcasterService


class FakeWebSocket:
    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(json.loads(message))


class TestWebSocketBroadcasterService(unittest.TestCase):
    def setUp(self):
        self.service = WebSocketBroadcasterService()
        self.auditor_one = FakeWebSocket()
        self.auditor_two = FakeWebSocket()

    def test_register_and_presence_broadcast(self):
        welcome = self.service.register_client(self.auditor_one)
        self.assertEqual(welcome["type"], "CONNECTION_ESTABLISHED")
        self.assertEqual(welcome["active_auditors"], 1)

        self.service.register_client(self.auditor_two)
        self.assertEqual(self.service.active_connections_count, 2)
        self.assertEqual(self.auditor_one.messages[-1]["type"], "PRESENCE_UPDATE")
        self.assertEqual(self.auditor_one.messages[-1]["data"]["active_auditors"], 2)

    def test_audit_note_is_broadcast_to_all_clients(self):
        self.service.register_client(self.auditor_one)
        self.service.register_client(self.auditor_two)
        raw = json.dumps({
            "type": "AUDIT_NOTE",
            "sender": "Auditor QA",
            "data": {
                "invoice_number": "F001-00012780",
                "note": "Validar diferencia de costo unitario.",
                "status": "OBSERVADO",
            },
        })

        event = self.service.process_incoming_message(self.auditor_one, raw)

        self.assertEqual(event["type"], "AUDIT_NOTE")
        self.assertEqual(event["data"]["invoice_number"], "F001-00012780")
        self.assertEqual(self.auditor_one.messages[-1]["type"], "AUDIT_NOTE")
        self.assertEqual(self.auditor_two.messages[-1]["data"]["status"], "OBSERVADO")

    def test_ping_returns_private_pong(self):
        pong = self.service.process_incoming_message(
            self.auditor_one,
            json.dumps({"type": "PING", "data": {"timestamp": 12345}}),
        )
        self.assertEqual(pong["type"], "PONG")
        self.assertEqual(pong["data"]["client_timestamp"], 12345)

    def test_invalid_json_returns_error(self):
        response = self.service.process_incoming_message(self.auditor_one, "not-json")
        self.assertEqual(response["type"], "ERROR")


if __name__ == "__main__":
    unittest.main()
