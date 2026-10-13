# -*- coding: utf-8 -*-
"""
Servicio de Validación mediante Expresiones Regulares (Regex).
Implementa reglas de negocio formales y validaciones sintácticas para documentos,
RUCs, códigos sanitarios, correos y montos en la capa de negocio.
"""
import re
from typing import Dict, Any, Tuple, Optional


class RegexValidatorService:
    """Servicio de negocio para validación de datos con Expresiones Regulares."""

    # 1. Número de Factura: Serie de 1 a 5 alfanuméricos, guion, y 4 a 8 dígitos correlativos
    #    Ejemplo: F002-00012780, FF78-0156780, F011-00089603
    INVOICE_NUMBER_PATTERN = re.compile(r"^[A-Z0-9]{1,5}-\d{4,8}$")

    # 2. RUC Proveedor (Perú): Exactamente 11 dígitos, iniciando con 10 (persona natural) o 20 (empresa)
    #    Ejemplo: 20100123456, 10458923412
    RUC_PATTERN = re.compile(r"^(10|20)\d{9}$")

    # 3. Código de Registro Sanitario: Prefijo farmacéutico (1 a 3 letras), guion, y código numérico
    #    Ejemplo: EE-04821, GN-12345, N-04123
    SANITARY_REG_PATTERN = re.compile(r"^[A-Z]{1,3}-\d{4,8}$")

    # 4. Fecha de Emisión: Formato estricto ISO YYYY-MM-DD con meses (01-12) y días (01-31)
    #    Ejemplo: 2026-06-15, 2026-12-31
    DATE_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")

    # 5. Correo Electrónico Corporativo: Estándar RFC 5322 simplificado
    #    Ejemplo: auditoria@farmacias.com.pe, proveedor@castillo.com
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    # 6. Importe Monetario: Número positivo con hasta 4 decimales opcionales
    #    Ejemplo: 1250.50, 45.8920, 100
    AMOUNT_PATTERN = re.compile(r"^\d+(\.\d{1,4})?$")

    # 7. Nombre de Archivo PDF: Caracteres válidos finalizados obligatoriamente en .pdf (case-insensitive)
    #    Ejemplo: F002-00012780 08.06.pdf, ALCON_F011.pdf
    PDF_FILENAME_PATTERN = re.compile(r"^[\w\s.-]+\.(pdf|PDF)$")

    PATTERNS: Dict[str, Dict[str, Any]] = {
        "invoice_number": {
            "regex": INVOICE_NUMBER_PATTERN,
            "desc_es": "Serie (1-5 letras/dígitos), guion y 4 a 8 dígitos (ej: F002-00012780)",
            "desc_en": "Series (1-5 letters/digits), hyphen and 4-8 digits (e.g.: F002-00012780)",
            "err_es": "Número de factura inválido. Debe cumplir con el formato: SERIE-NUMERO (ej: F002-00012780).",
            "err_en": "Invalid invoice number. Must match format: SERIES-NUMBER (e.g.: F002-00012780)."
        },
        "ruc": {
            "regex": RUC_PATTERN,
            "desc_es": "11 dígitos iniciando en 10 o 20 (ej: 20100123456)",
            "desc_en": "11 digits starting with 10 or 20 (e.g.: 20100123456)",
            "err_es": "RUC inválido. Debe tener exactamente 11 dígitos y comenzar con 10 o 20.",
            "err_en": "Invalid RUC. Must have exactly 11 digits starting with 10 or 20."
        },
        "sanitary_reg": {
            "regex": SANITARY_REG_PATTERN,
            "desc_es": "Prefijo de 1-3 letras, guion y 4 a 8 dígitos (ej: EE-04821)",
            "desc_en": "Prefix of 1-3 letters, hyphen and 4-8 digits (e.g.: EE-04821)",
            "err_es": "Registro sanitario inválido. Formato esperado: PREFIJO-NUMERO (ej: EE-04821).",
            "err_en": "Invalid sanitary registration. Expected format: PREFIX-NUMBER (e.g.: EE-04821)."
        },
        "invoice_date": {
            "regex": DATE_PATTERN,
            "desc_es": "Formato ISO AAAA-MM-DD (ej: 2026-06-15)",
            "desc_en": "ISO format YYYY-MM-DD (e.g.: 2026-06-15)",
            "err_es": "Fecha inválida. Debe tener formato AAAA-MM-DD con mes y día válidos (ej: 2026-06-15).",
            "err_en": "Invalid date. Must follow YYYY-MM-DD format with valid month and day (e.g.: 2026-06-15)."
        },
        "contact_email": {
            "regex": EMAIL_PATTERN,
            "desc_es": "Correo electrónico corporativo válido (ej: contacto@empresa.com)",
            "desc_en": "Valid corporate email address (e.g.: contact@company.com)",
            "err_es": "Correo electrónico inválido. Ingrese una dirección válida (ej: contacto@empresa.com).",
            "err_en": "Invalid email address. Please enter a valid email (e.g.: contact@company.com)."
        },
        "total_amount": {
            "regex": AMOUNT_PATTERN,
            "desc_es": "Número positivo con hasta 4 decimales (ej: 1250.50)",
            "desc_en": "Positive number with up to 4 decimals (e.g.: 1250.50)",
            "err_es": "Importe total inválido. Debe ser un número positivo con hasta 4 decimales.",
            "err_en": "Invalid total amount. Must be a positive number with up to 4 decimals."
        },
        "pdf_filename": {
            "regex": PDF_FILENAME_PATTERN,
            "desc_es": "Nombre de archivo finalizado en .pdf (ej: factura_01.pdf)",
            "desc_en": "File name ending in .pdf (e.g.: invoice_01.pdf)",
            "err_es": "Nombre de archivo inválido. El archivo debe finalizar obligatoriamente en .pdf.",
            "err_en": "Invalid file name. The file name must strictly end with .pdf."
        }
    }

    def validate_field(self, field_name: str, value: Optional[str], lang: str = "es") -> Tuple[bool, Optional[str]]:
        """
        Valida un campo individual contra su expresión regular.
        Retorna (is_valid, error_message).
        """
        if field_name not in self.PATTERNS:
            return True, None

        cfg = self.PATTERNS[field_name]
        val_str = str(value or "").strip()

        if not val_str:
            err = "El campo es obligatorio." if lang == "es" else "Field is required."
            return False, err

        if not cfg["regex"].match(val_str):
            err = cfg.get(f"err_{lang}") or cfg["err_es"]
            return False, err

        return True, None

    def validate_invoice_form(self, form_data: Dict[str, Any], lang: str = "es") -> Dict[str, Any]:
        """
        Valida el formulario completo de factura con Regex.
        Retorna diccionario con `is_valid`, `errors` y metadatos de validación.
        """
        errors: Dict[str, str] = {}
        validated_fields: Dict[str, bool] = {}

        for field_name in self.PATTERNS:
            val = form_data.get(field_name)
            is_valid, err_msg = self.validate_field(field_name, val, lang=lang)
            validated_fields[field_name] = is_valid
            if not is_valid and err_msg:
                errors[field_name] = err_msg

        return {
            "is_valid": len(errors) == 0,
            "total_fields": len(self.PATTERNS),
            "valid_fields_count": sum(1 for v in validated_fields.values() if v),
            "errors": errors,
            "validated_fields": validated_fields
        }

    def get_patterns_metadata(self, lang: str = "es") -> Dict[str, Any]:
        """Retorna las descripciones y patrones para inicializar la validación en el cliente."""
        meta = {}
        for k, v in self.PATTERNS.items():
            meta[k] = {
                "pattern": v["regex"].pattern,
                "description": v.get(f"desc_{lang}") or v["desc_es"],
                "error": v.get(f"err_{lang}") or v["err_es"]
            }
        return meta
