# -*- coding: utf-8 -*-
"""Capa de Acceso a Datos: Define repositorios y almacenamiento de documentos."""
from .interfaces import IInvoiceRepository, IAuditRepository, IDocumentStorage
from .excel_invoice_repo import ExcelInvoiceRepository
from .json_audit_repo import JsonAuditRepository
from .document_storage import DocumentStorage

__all__ = [
    "IInvoiceRepository",
    "IAuditRepository",
    "IDocumentStorage",
    "ExcelInvoiceRepository",
    "JsonAuditRepository",
    "DocumentStorage",
]
