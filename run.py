# -*- coding: utf-8 -*-
"""
Punto de Entrada Principal (Application Bootstrap & Dependency Injection).
Construye las capas de la arquitectura e inicia el servidor web.

Flujo de Inyección de Dependencias:
1. Configuración -> 2. Repositorios (Data Access) -> 3. Servicios (Business Logic) -> 4. Controladores (Presentation).
"""
import os
import socket
import webbrowser
from pathlib import Path
from flask import Flask, session, request, redirect, url_for
from flask_sock import Sock

from config import Config
from src.data_access import ExcelInvoiceRepository, JsonAuditRepository, DocumentStorage
from src.business import (
    AuthService,
    InvoiceService,
    AuditService,
    I18nService,
    RegexValidatorService,
    WebSocketBroadcasterService,
)
from src.presentation.controllers import auth_bp, invoice_bp, audit_bp, view_bp, register_websocket_routes


def create_app(config_class=Config) -> Flask:
    """
    Fábrica de aplicaciones (Application Factory Pattern).
    Inicializa Flask, cablea las dependencias entre capas y registra los Blueprints.
    """
    base_dir = Path(__file__).resolve().parent
    template_dir = base_dir / "src" / "presentation" / "templates"
    static_dir = base_dir / "src" / "presentation" / "static"

    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
        static_url_path="/static"
    )
    app.secret_key = config_class.SECRET_KEY

    # -------------------------------------------------------------
    # 1. Capa de Acceso a Datos (Data Access Layer - Repositorios)
    # -------------------------------------------------------------
    invoice_repo = ExcelInvoiceRepository(
        cache_json_path=config_class.INVOICE_DATA_CACHE,
        excel_path=config_class.EXCEL_PATH
    )
    audit_repo = JsonAuditRepository(
        json_path=config_class.AUDIT_DATA_CACHE
    )
    doc_storage = DocumentStorage(
        base_dir=config_class.WORKSPACE_DIR
    )

    # -------------------------------------------------------------
    # 2. Capa de Lógica de Negocio (Business Layer - Servicios)
    # -------------------------------------------------------------
    auth_service = AuthService(
        valid_username=config_class.DASHBOARD_USER,
        valid_password=config_class.DASHBOARD_PASSWORD
    )
    invoice_service = InvoiceService(
        invoice_repo=invoice_repo,
        doc_storage=doc_storage
    )
    audit_service = AuditService(
        audit_repo=audit_repo
    )
    i18n_service = I18nService(
        default_lang="es"
    )
    validator_service = RegexValidatorService()
    websocket_service = WebSocketBroadcasterService()

    # Inyección en el contexto de la aplicación
    app.auth_service = auth_service
    app.invoice_service = invoice_service
    app.audit_service = audit_service
    app.i18n_service = i18n_service
    app.validator_service = validator_service
    app.websocket_service = websocket_service

    # -------------------------------------------------------------
    # Soporte de Internacionalización (i18n) para Plantillas
    # -------------------------------------------------------------
    @app.before_request
    def detect_language():
        # Permitir cambiar idioma vía query param ?lang=en o ?lang=es
        lang_param = request.args.get("lang")
        if lang_param and app.i18n_service.is_supported(lang_param):
            session["lang"] = lang_param
        elif "lang" not in session:
            session["lang"] = app.i18n_service.default_lang

    @app.context_processor
    def inject_i18n():
        current_lang = session.get("lang", app.i18n_service.default_lang)
        def translate_helper(key, **kwargs):
            return app.i18n_service.translate(key, current_lang, **kwargs)

        return {
            "t": translate_helper,
            "current_lang": current_lang,
            "supported_languages": app.i18n_service.get_supported_languages(),
            "i18n_bundle": app.i18n_service.get_translations_bundle(current_lang)
        }

    @app.route("/set-lang/<lang_code>")
    def set_language(lang_code):
        if app.i18n_service.is_supported(lang_code):
            session["lang"] = lang_code
        target = request.args.get("next") or request.referrer or url_for("views.dashboard")
        return redirect(target)

    @app.route("/healthz")
    def healthcheck():
        """Comprobación HTTP liviana para la plataforma de despliegue."""
        return {"status": "ok", "websocket_path": "/ws/audit"}

    # -------------------------------------------------------------
    # 3. Capa de Presentación (Presentation Layer - Controladores)
    # -------------------------------------------------------------
    app.register_blueprint(auth_bp)
    app.register_blueprint(invoice_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(view_bp)

    # Flask-Sock mantiene una conexión full-duplex independiente de las APIs REST.
    sock = Sock(app)
    register_websocket_routes(sock)

    return app


# Objeto WSGI consumido por Gunicorn en producción.
app = create_app(Config)


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def main():
    port = Config.PORT
    debug = Config.DEBUG
    ip = get_local_ip()

    print("=" * 70)
    print("  DASHBOARD GS — ARQUITECTURA EN CAPAS (N-LAYER ARCHITECTURE)")
    print("  Curso: Tecnologías de Construcción de Software")
    print("  Soporte Multilingüe (i18n): Español (es) | English (en)")
    print("=" * 70)
    print(f"  > Servidor local:    http://localhost:{port}/")
    print(f"  > En la red local:   http://{ip}:{port}/")
    print(f"  > Usuario inicial:   {Config.DASHBOARD_USER}")
    print(f"  > Password inicial:  {Config.DASHBOARD_PASSWORD}")
    print("=" * 70)

    try:
        webbrowser.open(f"http://localhost:{port}/")
    except Exception:
        pass

    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
