# -*- coding: utf-8 -*-
"""
Servicio de lógica de negocio para Facturas y Costos de Medicamentos.
Implementa algoritmos de filtrado, búsqueda difusa, ordenamiento,
cálculo de inconsistencias y orquestación de acceso a datos.
"""
import re
import unicodedata
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from ..domain.models import InvoiceItem, InvoiceIndicators
from ..domain.dtos import InvoiceFilterDTO, PaginatedResultDTO
from ..data_access.interfaces import IInvoiceRepository, IDocumentStorage


def _strip_accents(s: Optional[str]) -> str:
    if s is None:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c)
    )


def _norm_text(s: Optional[str]) -> str:
    """Normaliza texto para búsqueda: sin acentos, minúsculas, espacios simples."""
    s = _strip_accents(s).lower()
    s = re.sub(r"[^a-z0-9%.,/\-]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


class InvoiceService:
    """Servicio de aplicación para la gestión y consulta de facturas."""

    def __init__(self, invoice_repo: IInvoiceRepository, doc_storage: IDocumentStorage):
        self.invoice_repo = invoice_repo
        self.doc_storage = doc_storage

    def get_providers(self) -> List[str]:
        """Obtiene lista ordenada de proveedores."""
        return self.invoice_repo.get_providers()

    def get_indicators(self) -> InvoiceIndicators:
        """Obtiene indicadores del negocio sobre facturas."""
        return self.invoice_repo.get_indicators()

    def get_metadata(self) -> Dict[str, Any]:
        """Obtiene metadatos del origen de datos."""
        return self.invoice_repo.get_metadata()

    def get_invoice_by_id(self, invoice_id: int) -> Optional[InvoiceItem]:
        """Obtiene detalle de una factura específica."""
        return self.invoice_repo.get_by_id(invoice_id)

    def resolve_pdf_path(self, relative_path: str) -> Optional[Path]:
        """Resuelve de forma segura el path físico del PDF."""
        return self.doc_storage.resolve_path(relative_path)

    def search_invoices(self, filters: InvoiceFilterDTO) -> PaginatedResultDTO:
        """
        Aplica reglas de negocio de búsqueda, filtros combinados,
        clasificación por inconsistencias y paginación.
        """
        all_invoices = self.invoice_repo.get_all()
        matched = all_invoices

        # 1. Filtro por búsqueda de texto de medicamento
        if filters.query:
            query_norm = _norm_text(filters.query)
            tokens = [t for t in query_norm.split() if t]
            if tokens:
                matched = [
                    inv for inv in matched
                    if all(t in _norm_text(inv.producto) for t in tokens)
                ]

        # 2. Filtro por Proveedor
        if filters.proveedor:
            prov_norm = filters.proveedor.strip().upper()
            matched = [inv for inv in matched if inv.proveedor.strip().upper() == prov_norm]

        # 3. Filtro por Fecha Desde
        if filters.fecha_desde:
            matched = [inv for inv in matched if inv.fecha and inv.fecha >= filters.fecha_desde]

        # 4. Filtro por Fecha Hasta
        if filters.fecha_hasta:
            matched = [inv for inv in matched if inv.fecha and inv.fecha <= filters.fecha_hasta]

        # 5. Filtro por Estado de PDF
        if filters.estado_pdf:
            matched = [inv for inv in matched if inv.pdf_status == filters.estado_pdf]

        # 6. Filtro por Número de Documento
        if filters.documento:
            doc_q = _norm_text(filters.documento)
            matched = [inv for inv in matched if doc_q in _norm_text(inv.documento)]

        # 7. Filtro por Nombre de Archivo PDF
        if filters.archivo_pdf:
            arc_q = _norm_text(filters.archivo_pdf)
            matched = [
                inv for inv in matched
                if inv.pdf_rel and arc_q in _norm_text(inv.pdf_rel)
            ]

        # 8. Filtro por Inconsistencias específicas
        if filters.problema_tipo:
            if filters.problema_tipo == "no_pdf":
                matched = [inv for inv in matched if inv.pdf_status in ("no_encontrado", "posible")]
            elif filters.problema_tipo == "sin_costo":
                matched = [inv for inv in matched if "sin_costo" in inv.problemas]
            elif filters.problema_tipo == "duplicado":
                matched = [inv for inv in matched if "duplicado_excel" in inv.problemas]
            elif filters.problema_tipo == "fecha_invalida":
                matched = [inv for inv in matched if "fecha_invalida" in inv.problemas]

        # Ordenamiento
        sort_key = filters.sort_key or "fecha"
        reverse = (filters.sort_dir == -1)

        def get_sort_val(inv: InvoiceItem):
            val = getattr(inv, sort_key, None)
            if val is None:
                return "" if isinstance(val, str) else 0
            return val

        try:
            matched.sort(key=get_sort_val, reverse=reverse)
        except Exception:
            pass

        total_count = len(matched)
        page_size = max(1, filters.page_size)
        total_pages = (total_count + page_size - 1) // page_size

        # Paginación
        start_idx = filters.page * page_size
        end_idx = start_idx + page_size
        page_items = [inv.to_dict() for inv in matched[start_idx:end_idx]]

        return PaginatedResultDTO(
            items=page_items,
            total_count=total_count,
            page=filters.page,
            page_size=page_size,
            total_pages=total_pages,
            meta={
                "sort_key": sort_key,
                "sort_dir": filters.sort_dir,
            }
        )
