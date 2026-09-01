# -*- coding: utf-8 -*-
"""
Data Transfer Objects (DTOs) para la comunicación entre capas.
Permiten transportar parámetros de búsqueda, filtros y respuestas paginadas.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict


@dataclass
class InvoiceFilterDTO:
    """Filtros para la búsqueda de facturas."""
    query: Optional[str] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    proveedor: Optional[str] = None
    estado_pdf: Optional[str] = None
    documento: Optional[str] = None
    archivo_pdf: Optional[str] = None
    problema_tipo: Optional[str] = None  # 'duplicado', 'sin_costo', 'fecha_invalida', 'no_pdf'
    page: int = 0
    page_size: int = 60
    sort_key: str = "fecha"
    sort_dir: int = -1  # 1 ascendente, -1 descendente


@dataclass
class AuditFilterDTO:
    """Filtros para la auditoría de precios."""
    query: Optional[str] = None
    proveedor: Optional[str] = None
    estado: Optional[str] = None  # 'sin_factura', 'topado', 'sin_ikf', 'revisar_match'
    margen_categoria: Optional[str] = None  # 'neg', 'low', 'ok', 'na'
    page: int = 0
    page_size: int = 60
    sort_key: str = "nombre"
    sort_dir: int = 1


@dataclass
class PaginatedResultDTO:
    """Resultado paginado genérico para transferir entre la capa de negocio y la de presentación."""
    items: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": self.items,
            "total_count": self.total_count,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
            "meta": self.meta,
        }
