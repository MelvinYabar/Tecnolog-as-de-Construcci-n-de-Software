# -*- coding: utf-8 -*-
"""
Implementación del almacenamiento de documentos.
Garantiza el acceso seguro a los archivos PDF de facturas (previniendo Directory Traversal).
"""
import os
from pathlib import Path
from typing import Optional

from .interfaces import IDocumentStorage


class DocumentStorage(IDocumentStorage):
    """Gestor de almacenamiento para archivos de facturas PDF."""

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir).resolve()

    def resolve_path(self, relative_path: str) -> Optional[Path]:
        """Resuelve la ruta relativa y valida que permanezca dentro del directorio permitido."""
        if not relative_path:
            return None
        
        # Limpiar separadores y normalizar
        cleaned = relative_path.lstrip("/\\")
        target_path = (self.base_dir / cleaned).resolve()

        # Validación de seguridad contra path traversal
        try:
            target_path.relative_to(self.base_dir)
        except ValueError:
            # Intento de escape de directorio
            return None

        if target_path.exists() and target_path.is_file():
            return target_path

        return None

    def file_exists(self, relative_path: str) -> bool:
        path = self.resolve_path(relative_path)
        return path is not None and path.exists()
