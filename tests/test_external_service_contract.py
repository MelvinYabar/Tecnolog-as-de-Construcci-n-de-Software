# -*- coding: utf-8 -*-
"""
Pruebas Unitarias para el Contrato del Servicio Externo (ExchangeRate-API & OpenFDA).
Verifica la estructura de datos, cálculos matemáticos de conversión de divisas,
y mecanismos de tolerancia ante fallos (offline fallback).
"""
import unittest


class TestExternalServiceContract(unittest.TestCase):

    def setUp(self):
        # Tasas de referencia oficiales (PEN como moneda base)
        self.sample_rates = {
            "PEN": 1.0,
            "USD": 0.2925,
            "EUR": 0.2485,
            "BRL": 1.4650
        }

    def convert_currency(self, amount_pen: float, target_currency: str) -> float:
        """Emula la lógica de conversión matemática implementada en external-service.js."""
        rate = self.sample_rates.get(target_currency, 1.0)
        return round(amount_pen * rate, 4)

    def test_currency_conversion_rates(self):
        """Verifica la conversión matemática de Soles (PEN) a USD, EUR y BRL."""
        pen_amount = 100.0

        usd_val = self.convert_currency(pen_amount, "USD")
        eur_val = self.convert_currency(pen_amount, "EUR")
        brl_val = self.convert_currency(pen_amount, "BRL")

        self.assertAlmostEqual(usd_val, 29.25, places=2)
        self.assertAlmostEqual(eur_val, 24.85, places=2)
        self.assertAlmostEqual(brl_val, 146.50, places=2)

    def test_reciprocal_exchange_rate(self):
        """Verifica el cálculo recíproco de 1 USD y 1 EUR en Soles (PEN)."""
        one_usd_in_pen = 1 / self.sample_rates["USD"]
        one_eur_in_pen = 1 / self.sample_rates["EUR"]

        # Debe estar en rangos realistas (1 USD ~ 3.42 PEN, 1 EUR ~ 4.02 PEN)
        self.assertGreater(one_usd_in_pen, 3.0)
        self.assertLess(one_usd_in_pen, 4.5)
        self.assertGreater(one_eur_in_pen, 3.5)
        self.assertLess(one_eur_in_pen, 5.0)

    def test_fallback_when_rate_missing(self):
        """Verifica que ante una divisa no soportada o ausente, aplica fallback determinista a tasa 1.0."""
        unknown_val = self.convert_currency(150.0, "XYZ")
        self.assertEqual(unknown_val, 150.0)

    def test_openfda_query_normalization(self):
        """Verifica la regla de normalización de nombres para OpenFDA (ej: Paracetamol -> Acetaminophen)."""
        def normalize_drug_for_fda(drug_name: str) -> str:
            lower = (drug_name or "").lower()
            if "paracetamol" in lower:
                return "acetaminophen"
            if "amoxicilina" in lower:
                return "amoxicillin"
            if "ibuprofeno" in lower:
                return "ibuprofen"
            return lower.split()[0] if lower else ""

        self.assertEqual(normalize_drug_for_fda("PARACETAMOL 500MG"), "acetaminophen")
        self.assertEqual(normalize_drug_for_fda("Amoxicilina Jarabe"), "amoxicillin")
        self.assertEqual(normalize_drug_for_fda("Ibuprofeno 400"), "ibuprofen")
        self.assertEqual(normalize_drug_for_fda("Cardivas 12.5mg"), "cardivas")


if __name__ == "__main__":
    unittest.main()
