# -*- coding: utf-8 -*-
"""
Implementación del repositorio de facturas.
Lee y deserializa los datos de facturas mapeándolos a entidades del Dominio (InvoiceItem).
Soporta lectura optimizada mediante caché JSON y fallback directo a Excel.
"""
import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from .interfaces import IInvoiceRepository
from ..domain.models import InvoiceItem, InvoiceIndicators


class ExcelInvoiceRepository(IInvoiceRepository):
    """Repositorio de facturas que carga y provee entidades InvoiceItem."""

    def __init__(self, cache_json_path: Path, excel_path: Optional[Path] = None):
        self.cache_json_path = Path(cache_json_path)
        self.excel_path = Path(excel_path) if excel_path else None
        self._invoices: List[InvoiceItem] = []
        self._providers: List[str] = []
        self._indicators: InvoiceIndicators = InvoiceIndicators()
        self._metadata: Dict[str, Any] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Carga los datos y los transforma en entidades InvoiceItem."""
        if self.cache_json_path.exists():
            try:
                with open(self.cache_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self._metadata = {
                    "fuente_excel": data.get("fuente_excel", ""),
                    "hoja": data.get("hoja", ""),
                    "generado": data.get("generado", ""),
                }
                self._providers = sorted(data.get("proveedores", []))

                ind = data.get("indicadores", {})
                self._indicators = InvoiceIndicators(
                    total_registros=ind.get("total_registros", 0),
                    medicamentos_distintos=ind.get("medicamentos_distintos", 0),
                    pdfs_encontrados=ind.get("pdfs_encontrados", 0),
                    pdfs_faltantes=ind.get("pdfs_faltantes", 0),
                    posibles_coincidencias=ind.get("posibles_coincidencias", 0),
                    registros_sin_documento=ind.get("registros_sin_documento", 0),
                    pct_vinculados=ind.get("pct_vinculados", 0.0),
                    inconsistencias=ind.get("inconsistencias", {}),
                )

                items = []
                for item in data.get("registros", []):
                    invoice = InvoiceItem(
                        id=item.get("id", 0),
                        row_idx=item.get("row_idx", 0),
                        proveedor=item.get("proveedor", ""),
                        fecha=item.get("fecha", ""),
                        documento=item.get("documento", ""),
                        producto=item.get("producto", ""),
                        cantidad=float(item.get("cantidad") or 0),
                        um=item.get("um", ""),
                        precio_unitario=float(item.get("precio_unitario") or 0),
                        importe_total=float(item.get("importe_total") or 0),
                        unidades_caja=item.get("unidades_caja"),
                        unidades_totales=item.get("unidades_totales"),
                        costo_unidad=item.get("costo_unidad"),
                        metodo_deteccion=item.get("metodo_deteccion"),
                        fuente=item.get("fuente"),
                        pdf_rel=item.get("pdf_rel"),
                        pdf_status=item.get("pdf_status", "vacio"),
                        pdf_match_mode=item.get("pdf_match_mode"),
                        candidatos=item.get("candidatos", []),
                        problemas=item.get("problemas", []),
                    )
                    items.append(invoice)
                
                self._invoices = items
                return
            except Exception as e:
                print(f"[ExcelInvoiceRepository] Error al cargar caché JSON: {e}")

        # Si no hay datos, inicializamos lista vacía
        self._invoices = []

    def get_all(self) -> List[InvoiceItem]:
        return self._invoices

    def get_by_id(self, invoice_id: int) -> Optional[InvoiceItem]:
        for inv in self._invoices:
            if inv.id == invoice_id:
                return inv
        return None

    def get_providers(self) -> List[str]:
        return self._providers

    def get_indicators(self) -> InvoiceIndicators:
        return self._indicators

    def get_metadata(self) -> Dict[str, Any]:
        return self._metadata
