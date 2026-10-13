# -*- coding: utf-8 -*-
"""
Configuración centralizada para la aplicación N-Layer.
Gestiona rutas del sistema, orígenes de datos y variables de entorno.
"""
import os
from pathlib import Path

# Raíz del workspace y del proyecto layered
CURRENT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = CURRENT_DIR.parent
BUNDLED_DATA_DIR = CURRENT_DIR / "data"


def _existing_or_bundled(existing_path: Path, bundled_name: str) -> Path:
    """Usa los datos del workspace local o el respaldo incluido para producción."""
    return existing_path if existing_path.exists() else BUNDLED_DATA_DIR / bundled_name

class Config:
    """Configuración base del sistema."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-layered-dashboard-2026")
    
    # Credenciales de acceso
    DASHBOARD_USER = os.environ.get("DASHBOARD_USER", "admin")
    DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "admin123")
    
    # Rutas a fuentes de datos originales
    WORKSPACE_DIR = WORKSPACE_ROOT if (WORKSPACE_ROOT / "COMPRAS").exists() else CURRENT_DIR
    COMPRAS_DIR = WORKSPACE_ROOT / "COMPRAS"
    EXCEL_PATH = WORKSPACE_ROOT / "exel" / "Costo real por unidad - desde facturas.xlsx"
    AUDIT_DATA_CACHE = Path(os.environ.get(
        "AUDIT_DATA_CACHE",
        _existing_or_bundled(WORKSPACE_ROOT / "dashboard_app" / "audit_data.json", "audit_data.json")
    ))
    INVOICE_DATA_CACHE = Path(os.environ.get(
        "INVOICE_DATA_CACHE",
        _existing_or_bundled(WORKSPACE_ROOT / "dashboard_app" / "data.json", "data.json")
    ))
    
    # Configuración de servidor
    PORT = int(os.environ.get("PORT", 8000))
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"


class TestingConfig(Config):
    """Configuración para entornos de pruebas unitarias."""
    TESTING = True
    DASHBOARD_USER = "test_user"
    DASHBOARD_PASSWORD = "test_password"
