# -*- coding: utf-8 -*-
"""Controladores y Blueprints de Flask."""
from .auth_controller import auth_bp
from .invoice_controller import invoice_bp
from .audit_controller import audit_bp
from .view_controller import view_bp
from .websocket_controller import register_websocket_routes

__all__ = ["auth_bp", "invoice_bp", "audit_bp", "view_bp", "register_websocket_routes"]
