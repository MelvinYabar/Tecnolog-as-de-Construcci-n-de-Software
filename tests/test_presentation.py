# -*- coding: utf-8 -*-
"""Pruebas de integración para la Capa de Presentación."""
import unittest
from run import create_app
from config import TestingConfig


class TestPresentationControllers(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

    def test_unauthenticated_redirect_to_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_login_page_renders(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Dashboard de Facturas y Costos".encode("utf-8"), response.data)

    def test_successful_login_and_access(self):
        # 1. Realizar login POST
        login_res = self.client.post("/login", data={
            "username": "test_user",
            "password": "test_password"
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b"Dashboard de Facturas y Costos", login_res.data)

        # 2. Consultar API de facturas autenticado
        api_res = self.client.get("/api/invoices/data")
        self.assertEqual(api_res.status_code, 200)
        self.assertTrue(api_res.is_json)


if __name__ == "__main__":
    unittest.main()
