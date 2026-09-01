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
from flask import Flask

from config import Config
from src.data_access import ExcelInvoiceRepository, JsonAuditRepository, DocumentStorage
from src.business import AuthService, InvoiceService, AuditService
from src.presentation.controllers import auth_bp, invoice_bp, audit_bp, view_bp


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

    # Inyección en el contexto de la aplicación
    app.auth_service = auth_service
    app.invoice_service = invoice_service
    app.audit_service = audit_service

    # -------------------------------------------------------------
    # 3. Capa de Presentación (Presentation Layer - Controladores)
    # -------------------------------------------------------------
    app.register_blueprint(auth_bp)
    app.register_blueprint(invoice_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(view_bp)

    return app


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
    app = create_app(Config)
    port = Config.PORT
    debug = Config.DEBUG
    ip = get_local_ip()

    print("=" * 70)
    print("  DASHBOARD GS — ARQUITECTURA EN CAPAS (N-LAYER ARCHITECTURE)")
    print("  Curso: Tecnologías de Construcción de Software")
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
