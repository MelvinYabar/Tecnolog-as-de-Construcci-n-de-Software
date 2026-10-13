# -*- coding: utf-8 -*-
"""
Pruebas Unitarias para Funciones STATELESS y STATEFUL.
Demuestra conceptual y programáticamente la diferencia entre funciones sin estado y con estado.
"""
import unittest
from pathlib import Path
from typing import List, Optional, Dict, Any

from src.domain.models import InvoiceItem, InvoiceIndicators
from src.data_access.interfaces import IInvoiceRepository, IDocumentStorage
from src.business.invoice_service import (
    InvoiceService,
    normalize_product_name_stateless,
    calculate_unit_cost_stateless
)


class DummyInvoiceRepo(IInvoiceRepository):
    def get_all(self) -> List[InvoiceItem]: return []
    def get_by_id(self, invoice_id: int) -> Optional[InvoiceItem]: return None
    def get_providers(self) -> List[str]: return []
    def get_indicators(self) -> InvoiceIndicators: return InvoiceIndicators()
    def get_metadata(self) -> Dict[str, Any]: return {}


class DummyDocStorage(IDocumentStorage):
    def resolve_path(self, relative_path: str) -> Optional[Path]: return None
    def file_exists(self, relative_path: str) -> bool: return False


class TestStatefulAndStatelessFunctions(unittest.TestCase):

    def setUp(self):
        self.service = InvoiceService(DummyInvoiceRepo(), DummyDocStorage())

    # ========================================================================
    # 1. PRUEBAS PARA FUNCIONES STATELESS (SIN ESTADO / PURAS)
    # ========================================================================

    def test_stateless_normalize_product_name(self):
        """
        Verifica que normalize_product_name_stateless es idempotente y determinista.
        Para las mismas entradas, siempre retorna el mismo valor sin depender de estado externo.
        """
        input_text = "  PARACETAMOL 500 mg (Caja x 100 Tab.) / Genérico  "
        expected = "paracetamol 500 mg caja x 100 tab. / generico"

        res1 = normalize_product_name_stateless(input_text)
        res2 = normalize_product_name_stateless(input_text)
        self.assertEqual(res1, expected)
        self.assertEqual(res1, res2, "Stateless: Siempre debe retornar el mismo resultado para la misma entrada")

    def test_stateless_calculate_unit_cost(self):
        """
        Verifica que calculate_unit_cost_stateless calcula costos matemáticamente sin side-effects.
        """
        # Caso normal
        self.assertEqual(calculate_unit_cost_stateless(150.0, 10.0), 15.0)
        self.assertEqual(calculate_unit_cost_stateless(100.0, 3.0), 33.3333)

        # Validación de parámetros inválidos (división por cero y negativos)
        self.assertIsNone(calculate_unit_cost_stateless(100.0, 0.0))
        self.assertIsNone(calculate_unit_cost_stateless(-50.0, 10.0))
        self.assertIsNone(calculate_unit_cost_stateless("invalido", 10.0))

    # ========================================================================
    # 2. PRUEBAS PARA FUNCIONES STATEFUL (CON ESTADO)
    # ========================================================================

    def test_stateful_track_invoice_view(self):
        """
        Verifica que track_invoice_view_stateful acumula estado en memoria.
        Llamadas sucesivas con el mismo invoice_id incrementan el contador (1 -> 2 -> 3).
        """
        invoice_id = 42

        count1 = self.service.track_invoice_view_stateful(invoice_id)
        self.assertEqual(count1, 1)

        count2 = self.service.track_invoice_view_stateful(invoice_id)
        self.assertEqual(count2, 2, "Stateful: El resultado depende del número de invocaciones previas")

        count3 = self.service.track_invoice_view_stateful(invoice_id)
        self.assertEqual(count3, 3)

        # Para otro invoice_id el estado es independiente
        other_count = self.service.track_invoice_view_stateful(99)
        self.assertEqual(other_count, 1)

    def test_stateful_add_search_history(self):
        """
        Verifica que add_search_history_stateful modifica el diccionario de sesión cronológicamente.
        """
        session_mock = {}

        # 1. Primera búsqueda
        h1 = self.service.add_search_history_stateful(session_mock, "amoxicilina")
        self.assertEqual(h1, ["amoxicilina"])
        self.assertEqual(session_mock["search_history"], ["amoxicilina"])

        # 2. Segunda búsqueda (se inserta al inicio)
        h2 = self.service.add_search_history_stateful(session_mock, "paracetamol")
        self.assertEqual(h2, ["paracetamol", "amoxicilina"])

        # 3. Tercera búsqueda repetida (se reubica al inicio sin duplicar)
        h3 = self.service.add_search_history_stateful(session_mock, "amoxicilina")
        self.assertEqual(h3, ["amoxicilina", "paracetamol"])


if __name__ == "__main__":
    unittest.main()
