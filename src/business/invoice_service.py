# -*- coding: utf-8 -*-
"""
Servicio de lógica de negocio para Facturas y Costos de Medicamentos.
Implementa algoritmos de filtrado, búsqueda difusa, ordenamiento,
cálculo de inconsistencias y orquestación de acceso a datos.

Incluye funciones explícitas STATELESS (sin estado) y STATEFUL (con estado)
para el curso de Tecnologías de Construcción de Software.
"""
import re
import unicodedata
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from ..domain.models import InvoiceItem, InvoiceIndicators
from ..domain.dtos import InvoiceFilterDTO, PaginatedResultDTO
from ..data_access.interfaces import IInvoiceRepository, IDocumentStorage


# ============================================================================
# FUNCIONES STATELESS (SIN ESTADO / PURAS)
# ============================================================================

def normalize_product_name_stateless(raw_name: Optional[str]) -> str:
    """
    [STATELESS 1] Normalización determinista de nombres de productos/medicamentos.
    
    Características Stateless:
    - Función pura: No depende ni modifica variables globales, archivos ni bases de datos.
    - Determinismo: Para un mismo `raw_name`, siempre retorna el mismo string normalizado.
    - Idempotencia y sin efectos secundarios (no side-effects).
    """
    if raw_name is None:
        return ""
    # Quitar acentos mediante descomposición Unicode NFKD
    text = "".join(
        c for c in unicodedata.normalize("NFKD", str(raw_name))
        if not unicodedata.combining(c)
    )
    text = text.lower()
    # Reemplazar caracteres no alfanuméricos por espacios
    text = re.sub(r"[^a-z0-9%.,/\-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def calculate_unit_cost_stateless(importe_total: float, unidades_totales: float) -> Optional[float]:
    """
    [STATELESS 2] Cálculo matemático puro de costo por unidad.
    
    Características Stateless:
    - No requiere memoria de ejecuciones pasadas ni estado de sesión.
    - Valida reglas aritméticas (división entre cero, valores negativos) puramente a partir de sus parámetros.
    - Retorna el costo redondeado a 4 decimales o None si los parámetros son inválidos.
    """
    try:
        total = float(importe_total)
        units = float(unidades_totales)
        if units <= 0 or total < 0:
            return None
        return round(total / units, 4)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


# ============================================================================
# SERVICIO PRINCIPAL
# ============================================================================

class InvoiceService:
    """Servicio de aplicación para la gestión y consulta de facturas."""

    def __init__(self, invoice_repo: IInvoiceRepository, doc_storage: IDocumentStorage):
        self.invoice_repo = invoice_repo
        self.doc_storage = doc_storage
        
        # [STATEFUL 1 - Almacén de estado]: Contador de visualizaciones en memoria
        self._view_counter: Dict[int, int] = {}

    # ========================================================================
    # FUNCIONES STATEFUL (CON ESTADO)
    # ========================================================================

    def track_invoice_view_stateful(self, invoice_id: int) -> int:
        """
        [STATEFUL 1] Registro y conteo acumulativo de visualizaciones de facturas.
        
        Características Stateful:
        - Modifica el estado interno persistido en memoria de la instancia (`self._view_counter`).
        - El valor de retorno cambia en cada llamada sucesiva para el mismo `invoice_id` (1, 2, 3...).
        - Mantiene métricas en tiempo de ejecución del sistema.
        """
        current_count = self._view_counter.get(invoice_id, 0) + 1
        self._view_counter[invoice_id] = current_count
        return current_count

    def get_invoice_view_count(self, invoice_id: int) -> int:
        """Consulta el estado actual de visualizaciones de una factura."""
        return self._view_counter.get(invoice_id, 0)

    @staticmethod
    def add_search_history_stateful(session_store: Dict[str, Any], query: str, max_items: int = 5) -> List[str]:
        """
        [STATEFUL 2] Gestión del historial de búsquedas del usuario en la sesión.
        
        Características Stateful:
        - Lee y muta el diccionario de sesión `session_store` que persiste entre peticiones HTTP.
        - Mantiene una lista FIFO de las últimas búsquedas únicas realizadas por el usuario actual.
        - El resultado devuelto depende de la secuencia cronológica previa de búsquedas.
        """
        if not query or not query.strip():
            return session_store.get("search_history", [])

        clean_q = query.strip()
        history: List[str] = session_store.get("search_history", [])

        # Evitar duplicados consecutivos y mantener orden reciente
        if clean_q in history:
            history.remove(clean_q)
        history.insert(0, clean_q)

        # Limitar al tamaño máximo
        history = history[:max_items]
        session_store["search_history"] = history
        return history

    # ========================================================================
    # MÉTODOS DE NEGOCIO Y CONSULTA
    # ========================================================================

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

        # 1. Filtro por búsqueda de texto de medicamento (usando función stateless)
        if filters.query:
            query_norm = normalize_product_name_stateless(filters.query)
            tokens = [t for t in query_norm.split() if t]
            if tokens:
                matched = [
                    inv for inv in matched
                    if all(t in normalize_product_name_stateless(inv.producto) for t in tokens)
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
            doc_q = normalize_product_name_stateless(filters.documento)
            matched = [inv for inv in matched if doc_q in normalize_product_name_stateless(inv.documento)]

        # 7. Filtro por Nombre de Archivo PDF
        if filters.archivo_pdf:
            arc_q = normalize_product_name_stateless(filters.archivo_pdf)
            matched = [
                inv for inv in matched
                if inv.pdf_rel and arc_q in normalize_product_name_stateless(inv.pdf_rel)
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
