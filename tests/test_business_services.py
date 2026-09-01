# -*- coding: utf-8 -*-
"""
Pruebas unitarias para la Capa de Lógica de Negocio.
Demuestra la alta testabilidad y aislamiento de los servicios mediante Mock Repositories.
"""
import unittest
from pathlib import Path
from typing import List, Optional, Dict, Any

from src.domain.models import InvoiceItem, ProductAudit, InvoiceIndicators, AuditIndicators
from src.domain.dtos import InvoiceFilterDTO, AuditFilterDTO
from src.data_access.interfaces import IInvoiceRepository, IAuditRepository, IDocumentStorage
from src.business.auth_service import AuthService
from src.business.invoice_service import InvoiceService
from src.business.audit_service import AuditService


class MockInvoiceRepository(IInvoiceRepository):
    """Mock para aislar pruebas del InvoiceService sin depender de disco."""

    def __init__(self, items: List[InvoiceItem]):
        self._items = items

    def get_all(self) -> List[InvoiceItem]:
        return self._items

    def get_by_id(self, invoice_id: int) -> Optional[InvoiceItem]:
        for i in self._items:
            if i.id == invoice_id:
                return i
        return None

    def get_providers(self) -> List[str]:
        return sorted(list({i.proveedor for i in self._items}))

    def get_indicators(self) -> InvoiceIndicators:
        return InvoiceIndicators(total_registros=len(self._items))

    def get_metadata(self) -> Dict[str, Any]:
        return {"fuente": "mock"}


class MockAuditRepository(IAuditRepository):
    """Mock para aislar pruebas del AuditService."""

    def __init__(self, records: List[ProductAudit]):
        self._records = records

    def get_all(self) -> List[ProductAudit]:
        return self._records

    def get_by_row_idx(self, row_idx: int) -> Optional[ProductAudit]:
        for r in self._records:
            if r.row_idx == row_idx:
                return r
        return None

    def get_providers(self) -> List[str]:
        return sorted(list({r.proveedor for r in self._records if r.proveedor}))

    def get_indicators(self) -> AuditIndicators:
        return AuditIndicators(total_productos=len(self._records))

    def get_metadata(self) -> Dict[str, Any]:
        return {"fuente": "mock"}


class MockDocumentStorage(IDocumentStorage):
    def resolve_path(self, relative_path: str) -> Optional[Path]:
        return Path("/mock/" + relative_path)

    def file_exists(self, relative_path: str) -> bool:
        return True


class TestBusinessServices(unittest.TestCase):

    def setUp(self):
        # Datos de prueba para facturas
        self.invoices = [
            InvoiceItem(id=1, row_idx=1, proveedor="DIMEXA", fecha="2026-05-10", documento="F001", producto="PARACETAMOL 500MG", cantidad=10, um="FCO", precio_unitario=5.0, importe_total=50.0, costo_unidad=5.0, pdf_status="encontrado"),
            InvoiceItem(id=2, row_idx=2, proveedor="ALFARO", fecha="2026-06-20", documento="F002", producto="AMOXICILINA 500MG", cantidad=20, um="TAB", precio_unitario=2.0, importe_total=40.0, costo_unidad=2.0, pdf_status="no_encontrado"),
            InvoiceItem(id=3, row_idx=3, proveedor="DIMEXA", fecha="2026-07-01", documento="F003", producto="PARACETAMOL JARABE", cantidad=5, um="FCO", precio_unitario=8.0, importe_total=40.0, costo_unidad=8.0, pdf_status="encontrado"),
        ]
        self.invoice_service = InvoiceService(MockInvoiceRepository(self.invoices), MockDocumentStorage())

        # Datos de prueba para auditoría
        self.audit_records = [
            ProductAudit(row_idx=1, nombre="PARACETAMOL 500MG", margen_pct=-0.10, precio_topado=True, sin_factura=False, proveedor="DIMEXA"),
            ProductAudit(row_idx=2, nombre="AMOXICILINA 500MG", margen_pct=0.25, precio_topado=False, sin_factura=True, proveedor="ALFARO"),
            ProductAudit(row_idx=3, nombre="IBUPROFENO 400MG", margen_pct=0.10, precio_topado=False, sin_factura=False, proveedor="DIMEXA"),
        ]
        self.audit_service = AuditService(MockAuditRepository(self.audit_records))

        self.auth_service = AuthService("admin", "secret123")

    def test_auth_service(self):
        user_ok = self.auth_service.authenticate("admin", "secret123")
        self.assertIsNotNone(user_ok)
        self.assertTrue(user_ok.is_authenticated)

        user_fail = self.auth_service.authenticate("admin", "wrong_password")
        self.assertIsNone(user_fail)

    def test_invoice_service_search_by_query(self):
        filters = InvoiceFilterDTO(query="paracetamol")
        res = self.invoice_service.search_invoices(filters)
        self.assertEqual(res.total_count, 2)

    def test_invoice_service_filter_by_provider(self):
        filters = InvoiceFilterDTO(proveedor="DIMEXA")
        res = self.invoice_service.search_invoices(filters)
        self.assertEqual(res.total_count, 2)

    def test_invoice_service_filter_by_pdf_status(self):
        filters = InvoiceFilterDTO(estado_pdf="no_encontrado")
        res = self.invoice_service.search_invoices(filters)
        self.assertEqual(res.total_count, 1)
        self.assertEqual(res.items[0]["documento"], "F002")

    def test_audit_service_filter_by_margin_neg(self):
        filters = AuditFilterDTO(margen_categoria="neg")
        res = self.audit_service.search_audit_products(filters)
        self.assertEqual(res.total_count, 1)
        self.assertEqual(res.items[0]["nombre"], "PARACETAMOL 500MG")

    def test_audit_service_filter_by_sin_factura(self):
        filters = AuditFilterDTO(estado="sin_factura")
        res = self.audit_service.search_audit_products(filters)
        self.assertEqual(res.total_count, 1)
        self.assertEqual(res.items[0]["nombre"], "AMOXICILINA 500MG")


if __name__ == "__main__":
    unittest.main()
