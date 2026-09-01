# -*- coding: utf-8 -*-
"""
Implementación del repositorio de auditoría de precios.
Lee y deserializa los registros de auditoría mapeándolos a entidades del Dominio (ProductAudit).
"""
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

from .interfaces import IAuditRepository
from ..domain.models import ProductAudit, AuditIndicators


class JsonAuditRepository(IAuditRepository):
    """Repositorio de auditoría de precios basado en JSON y fuentes de datos."""

    def __init__(self, json_path: Path):
        self.json_path = Path(json_path)
        self._audit_records: List[ProductAudit] = []
        self._providers: List[str] = []
        self._indicators: AuditIndicators = AuditIndicators()
        self._metadata: Dict[str, Any] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Carga y mapea los datos de auditoría a entidades ProductAudit."""
        if not self.json_path.exists():
            print(f"[JsonAuditRepository] Archivo {self.json_path} no encontrado.")
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._metadata = {
                "fuente": data.get("fuente", ""),
                "generado": data.get("generado", ""),
                "total": data.get("total", 0),
            }

            items = []
            providers_set = set()

            for x in data.get("productos", []):
                record = ProductAudit(
                    row_idx=x.get("row_idx", 0),
                    nombre=x.get("nombre", ""),
                    presentacion=x.get("presentacion", ""),
                    concentracion=x.get("concentracion"),
                    principio_activo=x.get("principio_activo"),
                    registro_sanitario=x.get("registro_sanitario"),
                    costo_lista=x.get("costo_lista"),
                    costo_lista_original=x.get("costo_lista_original"),
                    mediana=x.get("mediana"),
                    costo_descuento=x.get("costo_descuento"),
                    proveedor=x.get("proveedor"),
                    n_factura=x.get("n_factura"),
                    fecha_factura=x.get("fecha_factura"),
                    descuento_pct=x.get("descuento_pct"),
                    volumen_prom_mes=x.get("volumen_prom_mes"),
                    frecuencia_compras=x.get("frecuencia_compras"),
                    ikf_precio=x.get("ikf_precio"),
                    ikf_producto=x.get("ikf_producto"),
                    ikf_cantidad_envase=x.get("ikf_cantidad_envase"),
                    ikf_precio_unitario=x.get("ikf_precio_unitario"),
                    ikf_link=x.get("ikf_link"),
                    precio_recalculado=x.get("precio_recalculado"),
                    margen_pct=x.get("margen_pct"),
                    margen_fuente=x.get("margen_fuente"),
                    margen_atipico=bool(x.get("margen_atipico")),
                    precio_topado=bool(x.get("precio_topado")),
                    tope_sugerido=x.get("tope_sugerido"),
                    sin_factura=bool(x.get("sin_factura")),
                    match_score=x.get("match_score"),
                    ambiguous_note=x.get("ambiguous_note"),
                    no_cost_match=bool(x.get("no_cost_match")),
                )
                items.append(record)
                if record.proveedor:
                    providers_set.add(record.proveedor)

            self._audit_records = items
            self._providers = sorted(list(providers_set))
            self._compute_indicators()

        except Exception as e:
            print(f"[JsonAuditRepository] Error al cargar auditoría: {e}")

    def _compute_indicators(self) -> None:
        """Calcula indicadores clave del lote de auditoría."""
        sin_fac = sum(1 for r in self._audit_records if r.sin_factura)
        topados = sum(1 for r in self._audit_records if r.precio_topado)
        con_ikf = sum(1 for r in self._audit_records if r.ikf_precio is not None)
        
        m_neg = 0
        m_low = 0
        m_ok = 0
        m_na = 0

        for r in self._audit_records:
            if r.margen_pct is None:
                m_na += 1
            elif r.margen_pct < 0:
                m_neg += 1
            elif r.margen_pct <= 15:
                m_low += 1
            else:
                m_ok += 1

        self._indicators = AuditIndicators(
            total_productos=len(self._audit_records),
            sin_factura=sin_fac,
            precios_topados=topados,
            margen_negativo=m_neg,
            margen_bajo=m_low,
            margen_saludable=m_ok,
            sin_margen=m_na,
            con_inkafarma=con_ikf,
        )

    def get_all(self) -> List[ProductAudit]:
        return self._audit_records

    def get_by_row_idx(self, row_idx: int) -> Optional[ProductAudit]:
        for rec in self._audit_records:
            if rec.row_idx == row_idx:
                return rec
        return None

    def get_providers(self) -> List[str]:
        return self._providers

    def get_indicators(self) -> AuditIndicators:
        return self._indicators

    def get_metadata(self) -> Dict[str, Any]:
        return self._metadata
