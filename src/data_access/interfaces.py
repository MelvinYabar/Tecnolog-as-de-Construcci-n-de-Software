# -*- coding: utf-8 -*-
"""
Interfaces y contratos de la Capa de Acceso a Datos.
Define qué operaciones debe ofrecer la persistencia/origen de datos, permitiendo
sustituir implementaciones (Excel, SQL, MongoDB, Mock para tests) sin tocar la lógica de negocio.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
from ..domain.models import InvoiceItem, ProductAudit, InvoiceIndicators, AuditIndicators


class IInvoiceRepository(ABC):
    """Contrato para el repositorio de facturas y costos de medicamentos."""

    @abstractmethod
    def get_all(self) -> List[InvoiceItem]:
        """Obtiene todas las facturas cargadas en memoria/fuente."""
        pass

    @abstractmethod
    def get_by_id(self, invoice_id: int) -> Optional[InvoiceItem]:
        """Busca una factura por su identificador único."""
        pass

    @abstractmethod
    def get_providers(self) -> List[str]:
        """Obtiene la lista única de proveedores disponibles."""
        pass

    @abstractmethod
    def get_indicators(self) -> InvoiceIndicators:
        """Obtiene los indicadores estadísticos calculados de las facturas."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Obtiene metadatos del origen de datos (fuente, fecha de carga, etc.)."""
        pass


class IAuditRepository(ABC):
    """Contrato para el repositorio de auditoría de precios y márgenes."""

    @abstractmethod
    def get_all(self) -> List[ProductAudit]:
        """Obtiene todos los registros de auditoría de productos."""
        pass

    @abstractmethod
    def get_by_row_idx(self, row_idx: int) -> Optional[ProductAudit]:
        """Busca un registro de auditoría por su índice de fila original."""
        pass

    @abstractmethod
    def get_providers(self) -> List[str]:
        """Obtiene la lista de proveedores presentes en la auditoría."""
        pass

    @abstractmethod
    def get_indicators(self) -> AuditIndicators:
        """Obtiene los indicadores estadísticos de la auditoría."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Obtiene metadatos del origen de auditoría."""
        pass


class IDocumentStorage(ABC):
    """Contrato para la gestión y resolución segura de documentos y facturas PDF."""

    @abstractmethod
    def resolve_path(self, relative_path: str) -> Optional[Path]:
        """Resuelve una ruta relativa y verifica que sea segura y exista."""
        pass

    @abstractmethod
    def file_exists(self, relative_path: str) -> bool:
        """Verifica si existe el archivo solicitado."""
        pass
