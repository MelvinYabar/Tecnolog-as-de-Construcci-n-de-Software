# -*- coding: utf-8 -*-
"""
Controlador de Vistas Web.
Renderiza las plantillas Jinja2 y provee compatibilidad con endpoints web.
"""
from flask import Blueprint, render_template, redirect, url_for, session, current_app
from .auth_controller import login_required

view_bp = Blueprint("views", __name__)


@view_bp.route("/")
@login_required
def index():
    """Ruta raíz: redirige al dashboard principal."""
    return redirect(url_for("views.dashboard"))


@view_bp.route("/dashboard")
@view_bp.route("/dashboard_app/index.html")
@login_required
def dashboard():
    """Renderiza la vista principal del dashboard."""
    return render_template("index.html")


@view_bp.route("/demo-funciones")
@login_required
def demo_funciones():
    """Renderiza la vista de evidencia interactiva de funciones Stateful y Stateless."""
    service = current_app.invoice_service
    # Consultar estado de factura de demo (#42) y de sesión
    invoice_views = service.get_invoice_view_count(42)
    history = session.get("search_history", ["amoxicilina 500", "paracetamol"])
    return render_template(
        "demo_funciones.html",
        invoice_views=invoice_views,
        search_history=history
    )


@view_bp.route("/data.json")
@view_bp.route("/dashboard_app/data.json")
@login_required
def legacy_data_json():
    """Ruta de compatibilidad para data.json."""
    return redirect(url_for("invoices.get_full_invoice_data"))


@view_bp.route("/audit_data.json")
@view_bp.route("/dashboard_app/audit_data.json")
@login_required
def legacy_audit_data_json():
    """Ruta de compatibilidad para audit_data.json."""
    return redirect(url_for("audit.get_full_audit_data"))
