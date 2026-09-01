# -*- coding: utf-8 -*-
"""Pruebas unitarias para la Capa de Dominio."""
import unittest
from src.domain.models import InvoiceItem, ProductAudit, User, InvoiceIndicators


class TestDomainModels(unittest.TestCase):

    def test_user_entity(self):
        user = User(username="admin", is_authenticated=True)
        self.assertEqual(user.username, "admin")
        self.assertTrue(user.is_authenticated)

    def test_invoice_item_serialization(self):
        invoice = InvoiceItem(
            id=1,
            row_idx=10,
            proveedor="ALFARO S.A.",
            fecha="2026-06-15",
            documento="F001-00123",
            producto="PARACETAMOL 500 MG",
            cantidad=100.0,
            um="TAB",
            precio_unitario=0.20,
            importe_total=20.0,
            costo_unidad=0.20,
            pdf_status="encontrado"
        )
        d = invoice.to_dict()
        self.assertEqual(d["id"], 1)
        self.assertEqual(d["proveedor"], "ALFARO S.A.")
        self.assertEqual(d["pdf_status"], "encontrado")

    def test_product_audit_serialization(self):
        audit = ProductAudit(
            row_idx=1,
            nombre="ACICLOVIR 200MG",
            costo_lista=10.0,
            costo_descuento=8.0,
            margen_pct=-0.05,
            sin_factura=False
        )
        d = audit.to_dict()
        self.assertEqual(d["nombre"], "ACICLOVIR 200MG")
        self.assertEqual(d["margen_pct"], -0.05)
        self.assertFalse(d["sin_factura"])


if __name__ == "__main__":
    unittest.main()
