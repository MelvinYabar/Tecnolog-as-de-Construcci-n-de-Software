# -*- coding: utf-8 -*-
"""
Controlador de Facturas y Documentos.
Expone la API REST para búsqueda, métricas de facturas, visualización segura de PDFs,
y endpoints demostrativos de funciones STATELESS y STATEFUL.
"""
from flask import Blueprint, request, jsonify, send_file, abort, session, current_app
from .auth_controller import login_required
from ...domain.dtos import InvoiceFilterDTO
from ...business.invoice_service import calculate_unit_cost_stateless, normalize_product_name_stateless

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
    history = session.get("search_history", [])

    return jsonify({
        "fuente_excel": meta.get("fuente_excel", ""),
        "hoja": meta.get("hoja", ""),
        "generado": meta.get("generado", ""),
        "total_registros": len(invoices),
        "proveedores": providers,
        "indicadores": indicators,
        "search_history": history,
        "registros": invoices,
    })


@invoice_bp.route("/api/invoices/search", methods=["GET"])
@login_required
def search_invoices():
    """Búsqueda y filtrado paginado de facturas a través de la capa de negocio."""
    service = current_app.invoice_service
    query = request.args.get("q")

    # [STATEFUL 2] Registrar consulta en el historial de sesión
    if query and query.strip():
        service.add_search_history_stateful(session, query.strip())

    filters = InvoiceFilterDTO(
        query=query,
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


# ============================================================================
# ENDPOINTS STATELESS (Demostrativos)
# ============================================================================

@invoice_bp.route("/api/stateless/calculate-unit-cost", methods=["GET", "POST"])
@login_required
def api_stateless_calc_unit_cost():
    """
    Endpoint Stateless: Calcula el costo unitario sin almacenar ni depender de estado.
    Entrada: importe_total, unidades_totales
    """
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        importe = data.get("importe_total")
        unidades = data.get("unidades_totales")
    else:
        importe = request.args.get("importe_total")
        unidades = request.args.get("unidades_totales")

    result = calculate_unit_cost_stateless(importe, unidades)
    return jsonify({
        "type": "stateless_function",
        "importe_total": importe,
        "unidades_totales": unidades,
        "costo_unitario": result
    })


@invoice_bp.route("/api/stateless/normalize-text", methods=["GET"])
@login_required
def api_stateless_normalize():
    """
    Endpoint Stateless: Normaliza texto determinísticamente.
    Entrada: text
    """
    text = request.args.get("text", "")
    normalized = normalize_product_name_stateless(text)
    return jsonify({
        "type": "stateless_function",
        "original": text,
        "normalized": normalized
    })


# ============================================================================
# ENDPOINTS STATEFUL (Demostrativos)
# ============================================================================

@invoice_bp.route("/api/stateful/track-view/<int:invoice_id>", methods=["POST"])
@login_required
def api_stateful_track_view(invoice_id: int):
    """
    Endpoint Stateful: Incrementa y retorna el contador de visualizaciones en memoria.
    """
    service = current_app.invoice_service
    views = service.track_invoice_view_stateful(invoice_id)
    return jsonify({
        "type": "stateful_function",
        "invoice_id": invoice_id,
        "total_views": views
    })


@invoice_bp.route("/api/stateful/search-history", methods=["GET", "POST"])
@login_required
def api_stateful_search_history():
    """
    Endpoint Stateful: Consulta o agrega consultas al historial de sesión.
    """
    service = current_app.invoice_service
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        query = data.get("query", "")
        history = service.add_search_history_stateful(session, query)
    else:
        history = session.get("search_history", [])

    return jsonify({
        "type": "stateful_function",
        "search_history": history
    })


# ============================================================================
# VALIDACIÓN DE FORMULARIOS CON REGEX
# ============================================================================

@invoice_bp.route("/api/invoices/validate-form", methods=["POST"])
@login_required
def api_validate_invoice_form():
    """
    Endpoint para validar el formulario completo mediante Expresiones Regulares.
    Ejecuta las validaciones sintácticas en la capa de negocio.
    """
    data = request.get_json(silent=True) or {}
    lang = session.get("lang", current_app.i18n_service.default_lang)
    validator = current_app.validator_service
    result = validator.validate_invoice_form(data, lang=lang)
    return jsonify(result)


@invoice_bp.route("/api/invoices/regex-patterns", methods=["GET"])
@login_required
def api_get_regex_patterns():
    """
    Retorna los patrones Regex para sincronización cliente/servidor.
    """
    lang = session.get("lang", current_app.i18n_service.default_lang)
    validator = current_app.validator_service
    return jsonify({
        "lang": lang,
        "patterns": validator.get_patterns_metadata(lang=lang)
    })


# ============================================================================
# VISUALIZACIÓN DE DOCUMENTOS
# ============================================================================

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
