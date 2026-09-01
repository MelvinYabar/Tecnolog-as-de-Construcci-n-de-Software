# -*- coding: utf-8 -*-
"""
Servicio de lógica de negocio para Auditoría de Precios GS.
Implementa reglas de negocio para auditoría de márgenes, topes de precios y semáforos comerciales.
"""
import re
import unicodedata
from typing import List, Optional, Dict, Any

from ..domain.models import ProductAudit, AuditIndicators
from ..domain.dtos import AuditFilterDTO, PaginatedResultDTO
from ..data_access.interfaces import IAuditRepository


def _strip_accents(s: Optional[str]) -> str:
    if s is None:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c)
    )


def _norm_text(s: Optional[str]) -> str:
    s = _strip_accents(s).lower()
    s = re.sub(r"[^a-z0-9%.,/\-]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


class AuditService:
    """Servicio de aplicación para auditoría de precios y márgenes."""

    def __init__(self, audit_repo: IAuditRepository):
        self.audit_repo = audit_repo

    def get_providers(self) -> List[str]:
        return self.audit_repo.get_providers()

    def get_indicators(self) -> AuditIndicators:
        return self.audit_repo.get_indicators()

    def get_metadata(self) -> Dict[str, Any]:
        return self.audit_repo.get_metadata()

    def get_by_row_idx(self, row_idx: int) -> Optional[ProductAudit]:
        return self.audit_repo.get_by_row_idx(row_idx)

    def search_audit_products(self, filters: AuditFilterDTO) -> PaginatedResultDTO:
        """
        Aplica reglas de filtrado de auditoría, categorización de márgenes y paginación.
        """
        records = self.audit_repo.get_all()
        matched = records

        # 1. Filtro por nombre comercial o presentación
        if filters.query:
            q_norm = _norm_text(filters.query)
            tokens = [t for t in q_norm.split() if t]
            if tokens:
                matched = [
                    rec for rec in matched
                    if all(t in _norm_text(f"{rec.nombre} {rec.presentacion} {rec.principio_activo or ''}") for t in tokens)
                ]

        # 2. Filtro por Proveedor
        if filters.proveedor:
            prov_norm = filters.proveedor.strip().upper()
            matched = [
                rec for rec in matched
                if rec.proveedor and rec.proveedor.strip().upper() == prov_norm
            ]

        # 3. Filtro por Estado
        if filters.estado:
            if filters.estado == "sin_factura":
                matched = [rec for rec in matched if rec.sin_factura]
            elif filters.estado == "topado":
                matched = [rec for rec in matched if rec.precio_topado]
            elif filters.estado == "sin_ikf":
                matched = [rec for rec in matched if rec.ikf_precio is None]
            elif filters.estado == "revisar_match":
                matched = [
                    rec for rec in matched
                    if rec.match_score is not None and rec.match_score < 0.70
                ]

        # 4. Filtro por Categoría de Margen
        if filters.margen_categoria:
            if filters.margen_categoria == "neg":
                matched = [rec for rec in matched if rec.margen_pct is not None and rec.margen_pct < 0]
            elif filters.margen_categoria == "low":
                matched = [rec for rec in matched if rec.margen_pct is not None and 0 <= rec.margen_pct <= 15]
            elif filters.margen_categoria == "ok":
                matched = [rec for rec in matched if rec.margen_pct is not None and rec.margen_pct > 15]
            elif filters.margen_categoria == "na":
                matched = [rec for rec in matched if rec.margen_pct is None]

        # Ordenamiento
        sort_key = filters.sort_key or "nombre"
        reverse = (filters.sort_dir == -1)

        def get_sort_val(rec: ProductAudit):
            val = getattr(rec, sort_key, None)
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

        start_idx = filters.page * page_size
        end_idx = start_idx + page_size
        page_items = [rec.to_dict() for rec in matched[start_idx:end_idx]]

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
