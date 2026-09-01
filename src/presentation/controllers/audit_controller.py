# -*- coding: utf-8 -*-
"""
Controlador de Auditoría de Precios.
Expone la API REST para consulta y filtrado de registros de auditoría de precios y márgenes.
"""
from flask import Blueprint, request, jsonify, current_app
from .auth_controller import login_required
from ...domain.dtos import AuditFilterDTO

audit_bp = Blueprint("audit", __name__)


@audit_bp.route("/api/audit/data", methods=["GET"])
@login_required
def get_full_audit_data():
    """Retorna los datos completos estructurados de auditoría para el cliente web."""
    service = current_app.audit_service
    records = [rec.to_dict() for rec in service.audit_repo.get_all()]
    providers = service.get_providers()
    indicators = service.get_indicators().to_dict()
    meta = service.get_metadata()

    return jsonify({
        "fuente": meta.get("fuente", ""),
        "generado": meta.get("generado", ""),
        "total": len(records),
        "proveedores": providers,
        "indicadores": indicators,
        "productos": records,
    })


@audit_bp.route("/api/audit/search", methods=["GET"])
@login_required
def search_audit_products():
    """Búsqueda y filtrado paginado de productos en auditoría."""
    service = current_app.audit_service
    filters = AuditFilterDTO(
        query=request.args.get("q"),
        proveedor=request.args.get("proveedor"),
        estado=request.args.get("estado"),
        margen_categoria=request.args.get("margen_categoria"),
        page=int(request.args.get("page", 0)),
        page_size=int(request.args.get("page_size", 60)),
        sort_key=request.args.get("sort_key", "nombre"),
        sort_dir=int(request.args.get("sort_dir", 1)),
    )
    result = service.search_audit_products(filters)
    return jsonify(result.to_dict())
