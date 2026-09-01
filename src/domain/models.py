# -*- coding: utf-8 -*-
"""
Modelos y entidades del dominio.
Representan los conceptos clave del negocio sin acoplamiento a frameworks web o bases de datos.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class User:
    """Entidad de usuario para control de acceso y sesión."""
    username: str
    is_authenticated: bool = False


@dataclass
class InvoiceItem:
    """Entidad que representa una línea de detalle de factura de compra."""
    id: int
    row_idx: int
    proveedor: str
    fecha: str
    documento: str
    producto: str
    cantidad: float
    um: str
    precio_unitario: float
    importe_total: float
    unidades_caja: Optional[float] = None
    unidades_totales: Optional[float] = None
    costo_unidad: Optional[float] = None
    metodo_deteccion: Optional[str] = None
    fuente: Optional[str] = None
    pdf_rel: Optional[str] = None
    pdf_status: str = "vacio"  # 'encontrado', 'no_encontrado', 'posible', 'vacio'
    pdf_match_mode: Optional[str] = None
    candidatos: List[Dict[str, Any]] = field(default_factory=list)
    problemas: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entidad a un diccionario serializable."""
        return {
            "id": self.id,
            "row_idx": self.row_idx,
            "proveedor": self.proveedor,
            "fecha": self.fecha,
            "documento": self.documento,
            "producto": self.producto,
            "cantidad": self.cantidad,
            "um": self.um,
            "precio_unitario": self.precio_unitario,
            "importe_total": self.importe_total,
            "unidades_caja": self.unidades_caja,
            "unidades_totales": self.unidades_totales,
            "costo_unidad": self.costo_unidad,
            "metodo_deteccion": self.metodo_deteccion,
            "fuente": self.fuente,
            "pdf_rel": self.pdf_rel,
            "pdf_status": self.pdf_status,
            "pdf_match_mode": self.pdf_match_mode,
            "candidatos": self.candidatos,
            "problemas": self.problemas,
        }


@dataclass
class ProductAudit:
    """Entidad que representa un registro de auditoría de precios y márgenes de un producto."""
    row_idx: int
    nombre: str
    presentacion: str = ""
    concentracion: Optional[str] = None
    principio_activo: Optional[str] = None
    registro_sanitario: Optional[str] = None
    costo_lista: Optional[float] = None
    costo_lista_original: Optional[float] = None
    mediana: Optional[float] = None
    costo_descuento: Optional[float] = None
    proveedor: Optional[str] = None
    n_factura: Optional[str] = None
    fecha_factura: Optional[str] = None
    descuento_pct: Optional[float] = None
    volumen_prom_mes: Optional[float] = None
    frecuencia_compras: Optional[int] = None
    ikf_precio: Optional[float] = None
    ikf_producto: Optional[str] = None
    ikf_cantidad_envase: Optional[float] = None
    ikf_precio_unitario: Optional[float] = None
    ikf_link: Optional[str] = None
    precio_recalculado: Optional[float] = None
    margen_pct: Optional[float] = None
    margen_fuente: Optional[str] = None
    margen_atipico: bool = False
    precio_topado: bool = False
    tope_sugerido: Optional[float] = None
    sin_factura: bool = False
    match_score: Optional[float] = None
    ambiguous_note: Optional[str] = None
    no_cost_match: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el registro de auditoría a diccionario serializable."""
        return {
            "row_idx": self.row_idx,
            "nombre": self.nombre,
            "presentacion": self.presentacion,
            "concentracion": self.concentracion,
            "principio_activo": self.principio_activo,
            "registro_sanitario": self.registro_sanitario,
            "costo_lista": self.costo_lista,
            "costo_lista_original": self.costo_lista_original,
            "mediana": self.mediana,
            "costo_descuento": self.costo_descuento,
            "proveedor": self.proveedor,
            "n_factura": self.n_factura,
            "fecha_factura": self.fecha_factura,
            "descuento_pct": self.descuento_pct,
            "volumen_prom_mes": self.volumen_prom_mes,
            "frecuencia_compras": self.frecuencia_compras,
            "ikf_precio": self.ikf_precio,
            "ikf_producto": self.ikf_producto,
            "ikf_cantidad_envase": self.ikf_cantidad_envase,
            "ikf_precio_unitario": self.ikf_precio_unitario,
            "ikf_link": self.ikf_link,
            "precio_recalculado": self.precio_recalculado,
            "margen_pct": self.margen_pct,
            "margen_fuente": self.margen_fuente,
            "margen_atipico": self.margen_atipico,
            "precio_topado": self.precio_topado,
            "tope_sugerido": self.tope_sugerido,
            "sin_factura": self.sin_factura,
            "match_score": self.match_score,
            "ambiguous_note": self.ambiguous_note,
            "no_cost_match": self.no_cost_match,
        }


@dataclass
class InvoiceIndicators:
    """Métricas e indicadores globales de las facturas."""
    total_registros: int = 0
    medicamentos_distintos: int = 0
    pdfs_encontrados: int = 0
    pdfs_faltantes: int = 0
    posibles_coincidencias: int = 0
    registros_sin_documento: int = 0
    pct_vinculados: float = 0.0
    inconsistencias: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_registros": self.total_registros,
            "medicamentos_distintos": self.medicamentos_distintos,
            "pdfs_encontrados": self.pdfs_encontrados,
            "pdfs_faltantes": self.pdfs_faltantes,
            "posibles_coincidencias": self.posibles_coincidencias,
            "registros_sin_documento": self.registros_sin_documento,
            "pct_vinculados": self.pct_vinculados,
            "inconsistencias": self.inconsistencias,
        }


@dataclass
class AuditIndicators:
    """Métricas e indicadores globales de la auditoría de precios."""
    total_productos: int = 0
    sin_factura: int = 0
    precios_topados: int = 0
    margen_negativo: int = 0
    margen_bajo: int = 0
    margen_saludable: int = 0
    sin_margen: int = 0
    con_inkafarma: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_productos": self.total_productos,
            "sin_factura": self.sin_factura,
            "precios_topados": self.precios_topados,
            "margen_negativo": self.margen_negativo,
            "margen_bajo": self.margen_bajo,
            "margen_saludable": self.margen_saludable,
            "sin_margen": self.sin_margen,
            "con_inkafarma": self.con_inkafarma,
        }
