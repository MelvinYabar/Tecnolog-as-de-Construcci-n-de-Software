# -*- coding: utf-8 -*-
"""
Pruebas Unitarias para el Servicio de Validación con Expresiones Regulares (Regex).
Verifica patrones sintácticos formales, validaciones en español e inglés,
y endpoints de la API en la arquitectura N-Capas.
"""
import unittest
from src.business.validator_service import RegexValidatorService
from run import create_app
from config import TestingConfig


class TestRegexValidatorService(unittest.TestCase):

    def setUp(self):
        self.validator = RegexValidatorService()
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

    def test_invoice_number_regex(self):
        """Verifica el patrón de número de factura: SERIE (1-5 alfanuméricos) - CORRELATIVO (4-8 dígitos)."""
        valid_invoices = ["F002-00012780", "FF78-0156780", "F011-00089603", "E001-1234", "B1-12345678"]
        for inv in valid_invoices:
            is_valid, err = self.validator.validate_field("invoice_number", inv)
            self.assertTrue(is_valid, f"Debería ser válido: {inv}")
            self.assertIsNone(err)

        invalid_invoices = ["factura_01", "F00200012780", "TOOLONGSERIES-1234", "F1-123", "F1-123456789"]
        for inv in invalid_invoices:
            is_valid, err = self.validator.validate_field("invoice_number", inv)
            self.assertFalse(is_valid, f"Debería ser inválido: {inv}")
            self.assertIsNotNone(err)

    def test_ruc_regex(self):
        """Verifica el patrón de RUC peruano: 11 dígitos numéricos comenzando con 10 o 20."""
        valid_rucs = ["20100123456", "10458923412", "20543210987", "10876543210"]
        for ruc in valid_rucs:
            is_valid, err = self.validator.validate_field("ruc", ruc)
            self.assertTrue(is_valid, f"Debería ser válido: {ruc}")
            self.assertIsNone(err)

        invalid_rucs = ["30100123456", "2010012345", "201001234567", "20100ABC456", "102030"]
        for ruc in invalid_rucs:
            is_valid, err = self.validator.validate_field("ruc", ruc)
            self.assertFalse(is_valid, f"Debería ser inválido: {ruc}")
            self.assertIsNotNone(err)

    def test_sanitary_reg_regex(self):
        """Verifica el patrón de registro sanitario: PREFIJO (1-3 letras) - NÚMERO (4-8 dígitos)."""
        valid_regs = ["EE-04821", "GN-12345", "N-04123", "EN-00123456"]
        for reg in valid_regs:
            is_valid, err = self.validator.validate_field("sanitary_reg", reg)
            self.assertTrue(is_valid, f"Debería ser válido: {reg}")

        invalid_regs = ["12-04821", "EEEE-04821", "EE04821", "EE-123", "EE-ABCDEF"]
        for reg in invalid_regs:
            is_valid, err = self.validator.validate_field("sanitary_reg", reg)
            self.assertFalse(is_valid, f"Debería ser inválido: {reg}")

    def test_date_regex(self):
        """Verifica el formato ISO AAAA-MM-DD estricto para fechas."""
        valid_dates = ["2026-06-15", "2026-01-01", "2026-12-31", "2025-02-28"]
        for d in valid_dates:
            is_valid, err = self.validator.validate_field("invoice_date", d)
            self.assertTrue(is_valid, f"Debería ser válido: {d}")

        invalid_dates = ["15/06/2026", "2026-13-01", "2026-00-10", "2026-06-32", "2026-6-5"]
        for d in invalid_dates:
            is_valid, err = self.validator.validate_field("invoice_date", d)
            self.assertFalse(is_valid, f"Debería ser inválido: {d}")

    def test_email_regex(self):
        """Verifica el patrón de correo electrónico corporativo."""
        valid_emails = ["auditoria@farmacia.com", "contacto@castillo.com.pe", "user.name+tag@corp.net"]
        for email in valid_emails:
            is_valid, err = self.validator.validate_field("contact_email", email)
            self.assertTrue(is_valid, f"Debería ser válido: {email}")

        invalid_emails = ["sin-arroba.com", "@dominio.com", "usuario@", "usuario@.com"]
        for email in invalid_emails:
            is_valid, err = self.validator.validate_field("contact_email", email)
            self.assertFalse(is_valid, f"Debería ser inválido: {email}")

    def test_amount_regex(self):
        """Verifica montos numéricos positivos con hasta 4 decimales opcionales."""
        valid_amounts = ["100", "1250.50", "0.9999", "12450.75", "10.5"]
        for amt in valid_amounts:
            is_valid, err = self.validator.validate_field("total_amount", amt)
            self.assertTrue(is_valid, f"Debería ser válido: {amt}")

        invalid_amounts = ["-100", "1250.12345", "abc", "10,50", "12.34.56"]
        for amt in invalid_amounts:
            is_valid, err = self.validator.validate_field("total_amount", amt)
            self.assertFalse(is_valid, f"Debería ser inválido: {amt}")

    def test_pdf_filename_regex(self):
        """Verifica que el nombre de archivo finalice estrictamente en extensión .pdf o .PDF."""
        valid_pdfs = ["F002-00012780.pdf", "factura_08.06.PDF", "archivo con espacios.pdf", "doc-123.pdf"]
        for pdf in valid_pdfs:
            is_valid, err = self.validator.validate_field("pdf_filename", pdf)
            self.assertTrue(is_valid, f"Debería ser válido: {pdf}")

        invalid_pdfs = ["factura.docx", "archivo.xlsx", "sin_extension", "factura.pdf.exe"]
        for pdf in invalid_pdfs:
            is_valid, err = self.validator.validate_field("pdf_filename", pdf)
            self.assertFalse(is_valid, f"Debería ser inválido: {pdf}")

    def test_validate_invoice_form_success(self):
        """Verifica la validación exitosa de un formulario completo con datos válidos."""
        valid_payload = {
            "invoice_number": "F002-00012780",
            "ruc": "20100123456",
            "sanitary_reg": "EE-04821",
            "invoice_date": "2026-06-15",
            "contact_email": "auditoria@castillo.com.pe",
            "total_amount": "12450.75",
            "pdf_filename": "F002-00012780 08.06.pdf"
        }
        res = self.validator.validate_invoice_form(valid_payload, lang="es")
        self.assertTrue(res["is_valid"])
        self.assertEqual(len(res["errors"]), 0)
        self.assertEqual(res["valid_fields_count"], 7)

    def test_validate_invoice_form_with_errors(self):
        """Verifica la detección de múltiples errores de validación en el formulario."""
        invalid_payload = {
            "invoice_number": "invalido",
            "ruc": "12345",
            "sanitary_reg": "NO-REGISTRO",
            "invoice_date": "2026-99-99",
            "contact_email": "correo_malo",
            "total_amount": "-50",
            "pdf_filename": "archivo.txt"
        }
        res = self.validator.validate_invoice_form(invalid_payload, lang="es")
        self.assertFalse(res["is_valid"])
        self.assertEqual(len(res["errors"]), 7)
        self.assertIn("invoice_number", res["errors"])
        self.assertIn("ruc", res["errors"])
        self.assertIn("sanitary_reg", res["errors"])
        self.assertIn("invoice_date", res["errors"])
        self.assertIn("contact_email", res["errors"])
        self.assertIn("total_amount", res["errors"])
        self.assertIn("pdf_filename", res["errors"])

    def test_http_endpoint_validate_form(self):
        """Verifica el endpoint POST /api/invoices/validate-form."""
        # Con autenticación simulada (session)
        with self.client.session_transaction() as sess:
            sess["logged_in"] = True
            sess["username"] = "admin"
            sess["lang"] = "es"

        valid_payload = {
            "invoice_number": "F002-00012780",
            "ruc": "20100123456",
            "sanitary_reg": "EE-04821",
            "invoice_date": "2026-06-15",
            "contact_email": "auditoria@castillo.com.pe",
            "total_amount": "12450.75",
            "pdf_filename": "F002-00012780 08.06.pdf"
        }
        response = self.client.post("/api/invoices/validate-form", json=valid_payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["is_valid"])
        self.assertEqual(data["valid_fields_count"], 7)

    def test_http_endpoint_regex_patterns(self):
        """Verifica el endpoint GET /api/invoices/regex-patterns."""
        with self.client.session_transaction() as sess:
            sess["logged_in"] = True
            sess["username"] = "admin"
            sess["lang"] = "es"

        response = self.client.get("/api/invoices/regex-patterns")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("patterns", data)
        self.assertIn("invoice_number", data["patterns"])
        self.assertIn("ruc", data["patterns"])


if __name__ == "__main__":
    unittest.main()
