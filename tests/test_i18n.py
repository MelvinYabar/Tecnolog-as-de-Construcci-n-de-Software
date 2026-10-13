# -*- coding: utf-8 -*-
"""
Pruebas Unitarias para el Servicio de Internacionalización (i18n).
Verifica traducciones en español e inglés, resolución de claves, fallback y endpoints HTTP.
"""
import unittest
from src.business.i18n_service import I18nService
from run import create_app
from config import TestingConfig


class TestI18nService(unittest.TestCase):

    def setUp(self):
        self.i18n = I18nService(default_lang="es")
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

    def test_translation_spanish(self):
        """Verifica traducciones en español (idioma por defecto)."""
        title = self.i18n.translate("app_title", lang="es")
        self.assertEqual(title, "Dashboard de Facturas y Costos de Medicamentos")

        records_lbl = self.i18n.translate("card_total_records", lang="es")
        self.assertEqual(records_lbl, "Registros analizados")

    def test_translation_english(self):
        """Verifica traducciones en inglés."""
        title = self.i18n.translate("app_title", lang="en")
        self.assertEqual(title, "Medicine Invoices and Costs Dashboard")

        records_lbl = self.i18n.translate("card_total_records", lang="en")
        self.assertEqual(records_lbl, "Analyzed records")

    def test_translation_fallback_to_default(self):
        """Verifica que si se pide un idioma no soportado o clave faltante, aplica fallback."""
        # Idioma no soportado hace fallback a default_lang (es)
        title = self.i18n.translate("app_title", lang="fr")
        self.assertEqual(title, "Dashboard de Facturas y Costos de Medicamentos")

        # Clave inexistente retorna la misma clave
        unknown = self.i18n.translate("non_existent_key_123", lang="en")
        self.assertEqual(unknown, "non_existent_key_123")

    def test_formatted_parameters(self):
        """Verifica parámetros dinámicos en strings traducidos."""
        res_es = self.i18n.translate("results_found", lang="es", count=42)
        self.assertEqual(res_es, "42 registro(s) encontrado(s)")

        res_en = self.i18n.translate("results_found", lang="en", count=42)
        self.assertEqual(res_en, "42 record(s) found")

    def test_http_language_switch(self):
        """Verifica el cambio de idioma vía ruta /set-lang/<code."""
        # 1. Por defecto o con ?lang=es
        res_es = self.client.get("/login?lang=es")
        self.assertIn("Iniciar sesión".encode("utf-8"), res_es.data)

        # 2. Cambiar a inglés vía /set-lang/en
        switch_res = self.client.get("/set-lang/en", follow_redirects=True)
        self.assertEqual(switch_res.status_code, 200)

        # 3. La página de login ahora debe estar en inglés
        res_en = self.client.get("/login")
        self.assertIn("Log In".encode("utf-8"), res_en.data)
        self.assertIn("Username".encode("utf-8"), res_en.data)


if __name__ == "__main__":
    unittest.main()
