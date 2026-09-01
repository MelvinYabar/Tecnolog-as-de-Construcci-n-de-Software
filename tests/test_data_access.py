# -*- coding: utf-8 -*-
"""Pruebas unitarias para la Capa de Acceso a Datos."""
import unittest
import tempfile
import os
from pathlib import Path

from src.data_access.document_storage import DocumentStorage


class TestDocumentStorage(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.test_dir.name)
        
        # Crear estructura de prueba
        self.compras_dir = self.base_path / "COMPRAS" / "ALFARO"
        self.compras_dir.mkdir(parents=True)
        self.dummy_pdf = self.compras_dir / "factura1.pdf"
        self.dummy_pdf.write_bytes(b"%PDF-1.4 dummy")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_resolve_valid_path(self):
        storage = DocumentStorage(self.base_path)
        resolved = storage.resolve_path("COMPRAS/ALFARO/factura1.pdf")
        self.assertIsNotNone(resolved)
        self.assertTrue(resolved.exists())
        self.assertEqual(resolved.name, "factura1.pdf")

    def test_prevent_directory_traversal(self):
        storage = DocumentStorage(self.base_path)
        # Intento malicioso de salir de la carpeta base
        resolved = storage.resolve_path("../../windows/system32/cmd.exe")
        self.assertIsNone(resolved)

    def test_non_existent_file(self):
        storage = DocumentStorage(self.base_path)
        resolved = storage.resolve_path("COMPRAS/ALFARO/no_existe.pdf")
        self.assertIsNone(resolved)


if __name__ == "__main__":
    unittest.main()
