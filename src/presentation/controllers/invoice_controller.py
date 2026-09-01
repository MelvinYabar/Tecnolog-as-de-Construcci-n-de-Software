# -*- coding: utf-8 -*-
"""
Controlador de Facturas y Documentos.
Expone la API REST para búsqueda, métricas de facturas y visualización segura de PDFs.
"""
from flask import Blueprint, request, jsonify, send_file, abort, current_app
from .auth_controller import login_required
from ...domain.dtos import InvoiceFilterDTO

invoice_bp = Blueprint("invoices", __name__)


@invoice_bp.route("/api/invoices/data", methods=["GET"])
@login_required
def get_full_invoice_data():
    """Retorna los datos completos estructurados para el cliente web."""
    service = current_app.invoice_service
    invoices = [inv.to_dict() for inv in service.invoice_repo.get_all()]
    providers = service.get_providers()
    indicators = service.get_indicators().to_dict()
    meta = service.get_metadata()

    return jsonify({
        "fuente_excel": meta.get("fuente_excel", ""),
        "hoja": meta.get("hoja", ""),
        "generado": meta.get("generado", ""),
        "total_registros": len(invoices),
        "proveedores": providers,
        "indicadores": indicators,
        "registros": invoices,
    })


@invoice_bp.route("/api/invoices/search", methods=["GET"])
@login_required
def search_invoices():
    """Búsqueda y filtrado paginado de facturas a través de la capa de negocio."""
    service = current_app.invoice_service
    filters = InvoiceFilterDTO(
        query=request.args.get("q"),
        fecha_desde=request.args.get("fecha_desde"),
        fecha_hasta=request.args.get("fecha_hasta"),
        proveedor=request.args.get("proveedor"),
        estado_pdf=request.args.get("estado_pdf"),
        documento=request.args.get("documento"),
        archivo_pdf=request.args.get("archivo_pdf"),
        problema_tipo=request.args.get("problema_tipo"),
        page=int(request.args.get("page", 0)),
        page_size=int(request.args.get("page_size", 60)),
        sort_key=request.args.get("sort_key", "fecha"),
        sort_dir=int(request.args.get("sort_dir", -1)),
    )
    result = service.search_invoices(filters)
    return jsonify(result.to_dict())


@invoice_bp.route("/COMPRAS/<path:filename>")
@invoice_bp.route("/api/documents/<path:filename>")
@login_required
def view_document(filename):
    """Visualización y descarga segura de facturas PDF."""
    service = current_app.invoice_service
    safe_path = service.resolve_pdf_path(filename)
    if not safe_path:
        abort(404)
    return send_file(safe_path, mimetype="application/pdf")
