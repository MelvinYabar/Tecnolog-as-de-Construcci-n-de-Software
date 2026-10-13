# -*- coding: utf-8 -*-
"""
Servicio de Internacionalización (i18n).
Gestiona catálogos de traducción multilingüe (Español, Inglés y Portugués) de forma desacoplada
para la arquitectura en capas.
"""
from typing import Dict, Any, List, Optional


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "es": {
        # General / Header
        "app_title": "Dashboard de Facturas y Costos de Medicamentos",
        "loading_data": "Cargando datos desde la Capa de Negocio...",
        "source_label": "Fuente: {source} — hoja \"{sheet}\" — generado {generated}",
        "tier_badge": "Arquitectura N-Capas (4-Tier)",
        "view_functions_btn": "★ Ver Funciones Stateful / Stateless",
        "btn_toggle_regex_form": "📋 Formulario de Validación Regex",
        "logout_btn": "Cerrar sesión",
        "login_title": "Iniciar sesión — Dashboard GS (N-Layer)",
        "login_heading": "Dashboard de Facturas y Costos GS",
        "login_sub": "Tecnologías de Construcción de Software",
        "username_label": "Usuario",
        "password_label": "Contraseña",
        "login_submit": "Iniciar Sesión",
        "login_error": "Usuario o contraseña incorrectos.",
        "lang_selector_label": "Idioma",

        # Metrics Cards
        "card_total_records": "Registros analizados",
        "card_distinct_meds": "Medicamentos distintos",
        "card_pdfs_found": "PDFs encontrados",
        "card_pdfs_missing": "PDFs faltantes",
        "card_possible_matches": "Posibles coincidencias",
        "card_no_doc_number": "Registros sin nº de documento",
        "card_pct_linked": "% vinculados a un PDF",

        # Filters
        "filter_title": "Buscar medicamento",
        "filter_query_label": "Nombre, parte del nombre, principio activo o concentración",
        "filter_query_placeholder": "Ej: paracetamol, amoxicilina 500, cardivas 12.5...",
        "filter_date_from": "Fecha desde",
        "filter_date_to": "Fecha hasta",
        "filter_provider": "Proveedor",
        "filter_all": "Todos",
        "filter_pdf_status": "Estado del PDF",
        "filter_status_found": "PDF encontrado",
        "filter_status_missing": "PDF no encontrado",
        "filter_status_possible": "Posible coincidencia",
        "filter_status_empty": "Sin número de documento",
        "filter_doc_number": "Número de factura",
        "filter_doc_placeholder": "Ej: F002-00012780",
        "filter_pdf_file": "Nombre de archivo PDF",
        "filter_pdf_placeholder": "Ej: F002-00012780 08.06.pdf",
        "btn_search": "Buscar",
        "btn_clear": "Limpiar filtros",
        "btn_only_issues": "Ver solo registros con problemas de PDF",
        "history_title": "Historial de búsquedas recientes (Estado de Sesión - Stateful):",
        "fuzzy_title": "¿Quizás buscaba? (Sugerencias calculadas - Stateless):",
        "fuzzy_empty": "No se encontraron coincidencias exactas ni variaciones cercanas para \"{query}\".",

        # Table
        "results_title": "Resultados",
        "results_found": "{count} registro(s) encontrado(s)",
        "filter_active_issue": " — filtro de inconsistencia activo",
        "th_date": "Fecha",
        "th_provider": "Proveedor",
        "th_invoice_no": "N° factura",
        "th_medicine": "Medicamento",
        "th_qty": "Cant.",
        "th_unit": "U.M.",
        "th_unit_price": "Precio unit.",
        "th_total_amount": "Importe total",
        "th_unit_cost": "Costo/unidad",
        "th_pdf_status": "Estado PDF",
        "page_info": "Página {current} de {total}",
        "btn_prev": "‹ Anterior",
        "btn_next": "Siguiente ›",

        # Detail Panel
        "detail_title": "Detalle del registro seleccionado",
        "detail_med": "Medicamento",
        "detail_provider": "Proveedor",
        "detail_date": "Fecha factura",
        "detail_doc": "N° factura",
        "detail_qty": "Cantidad",
        "detail_unit_price": "Precio unitario",
        "detail_total_amount": "Importe total",
        "detail_units_box": "Unidades/caja",
        "detail_total_units": "Unidades totales",
        "detail_unit_cost_stateless": "Costo por unidad (Stateless)",
        "detail_detection_method": "Método de detección",
        "detail_views_stateful": "Visualizaciones (Stateful)",
        "detail_source_sheet": "Fuente (hoja original)",
        "detail_pdf_status": "Estado PDF",
        "detail_open_new_tab": "Abrir en pestaña nueva",
        "detail_file_label": "Archivo: {path}",
        "detail_empty_selection": "Seleccione un registro para previsualizar su PDF.",
        "detail_empty_no_doc": "Este registro no tiene número de documento; no se puede buscar el PDF.",
        "detail_empty_not_found": "No se encontró un PDF que coincida con este registro.",
        "detail_multiple_matches": "Hay varias coincidencias posibles. Seleccione la correcta para previsualizar:",
        "views_badge": "👁 {count} vista(s)",

        # Inconsistencies
        "incons_title": "Reporte de inconsistencias",
        "incons_hint": "Haga clic en un indicador para filtrar la tabla con esos registros.",
        "inc_duplicate_rows": "Filas duplicadas",
        "inc_medicines_no_cost": "Medicamentos sin costo",
        "inc_invalid_dates": "Fechas vacías o inválidas",
        "inc_empty_docs": "Sin número de documento",
        "inc_missing_pdfs": "Archivos PDF faltantes",
        "inc_multiple_matches": "Con más de una posible coincidencia",

        # Regex Form
        "regex_form_title": "Validación de Documentos y Facturas con Expresiones Regulares (Regex)",
        "regex_form_sub": "Validación sintáctica y de reglas de negocio en capas cliente y servidor mediante patrones formales Regex.",
        "regex_field_invoice": "Número de Factura (Serie-Número)",
        "regex_field_ruc": "RUC del Proveedor (11 dígitos)",
        "regex_field_sanitary": "Registro Sanitario Farmacéutico",
        "regex_field_date": "Fecha de Emisión (AAAA-MM-DD)",
        "regex_field_email": "Correo Electrónico de Auditoría",
        "regex_field_amount": "Importe Total (S/)",
        "regex_field_pdf": "Nombre de Archivo PDF Adjunto",
        "regex_btn_validate": "Validar en Servidor (Capa de Negocio)",
        "regex_btn_fill_valid": "Cargar Ejemplo Válido",
        "regex_btn_fill_invalid": "Cargar Ejemplo con Errores",
        "regex_success_alert": "¡Formulario validado con éxito! Todos los campos cumplen con las Expresiones Regulares.",
        "regex_error_alert": "Se encontraron errores de validación. Por favor corrija los campos señalados en rojo.",
        "regex_pattern_badge": "Patrón:",
        "regex_valid_tag": "Válido",
        "regex_invalid_tag": "Inválido",

        # External Service & Component Diagram
        "btn_toggle_external_service": "🌐 Servicio Externo (Divisas)",
        "btn_view_component_diagram": "📐 Diagrama de Componentes",
        "ext_service_title": "Consumo de Servicio Externo en Tiempo Real (ExchangeRate-API & OpenFDA)",
        "ext_service_sub": "Consumo asíncrono directo desde el navegador (fetch REST) sin pasar por el servidor Flask.",
        "ext_ticker_label": "Tipo de Cambio en Vivo:",
        "ext_currency_label": "Moneda en Tabla:",
        "ext_status_online": "🟢 200 OK — En vivo desde el navegador",
        "ext_btn_refresh": "🔄 Actualizar Tasas",
        "ext_calc_title": "Calculadora de Conversión de Moneda en Vivo",
        "ext_fda_lookup_btn": "🔍 Consultar Fármaco en OpenFDA",
        "ext_json_viewer_title": "Payload JSON recibido directamente desde el servicio externo:",
        "modal_diagram_title": "Diagrama de Componentes UML (UML 2.5) — Arquitectura en Capas"
    },
    "en": {
        # General / Header
        "app_title": "Medicine Invoices and Costs Dashboard",
        "loading_data": "Loading data from Business Layer...",
        "source_label": "Source: {source} — sheet \"{sheet}\" — generated {generated}",
        "tier_badge": "N-Layer Architecture (4-Tier)",
        "view_functions_btn": "★ View Stateful / Stateless Functions",
        "btn_toggle_regex_form": "📋 Regex Validation Form",
        "logout_btn": "Log out",
        "login_title": "Log In — GS Dashboard (N-Layer)",
        "login_heading": "GS Invoices and Costs Dashboard",
        "login_sub": "Software Construction Technologies",
        "username_label": "Username",
        "password_label": "Password",
        "login_submit": "Log In",
        "login_error": "Invalid username or password.",
        "lang_selector_label": "Language",

        # Metrics Cards
        "card_total_records": "Analyzed records",
        "card_distinct_meds": "Distinct medicines",
        "card_pdfs_found": "PDFs found",
        "card_pdfs_missing": "Missing PDFs",
        "card_possible_matches": "Possible matches",
        "card_no_doc_number": "Records without doc number",
        "card_pct_linked": "% linked to a PDF",

        # Filters
        "filter_title": "Search medicine",
        "filter_query_label": "Name, partial name, active ingredient or concentration",
        "filter_query_placeholder": "E.g.: paracetamol, amoxicillin 500, cardivas 12.5...",
        "filter_date_from": "Date from",
        "filter_date_to": "Date to",
        "filter_provider": "Supplier",
        "filter_all": "All",
        "filter_pdf_status": "PDF Status",
        "filter_status_found": "PDF found",
        "filter_status_missing": "PDF not found",
        "filter_status_possible": "Possible match",
        "filter_status_empty": "Without document number",
        "filter_doc_number": "Invoice number",
        "filter_doc_placeholder": "E.g.: F002-00012780",
        "filter_pdf_file": "PDF file name",
        "filter_pdf_placeholder": "E.g.: F002-00012780 08.06.pdf",
        "btn_search": "Search",
        "btn_clear": "Clear filters",
        "btn_only_issues": "View only records with PDF issues",
        "history_title": "Recent search history (Session State - Stateful):",
        "fuzzy_title": "Did you mean? (Calculated suggestions - Stateless):",
        "fuzzy_empty": "No exact matches or close variations found for \"{query}\".",

        # Table
        "results_title": "Results",
        "results_found": "{count} record(s) found",
        "filter_active_issue": " — inconsistency filter active",
        "th_date": "Date",
        "th_provider": "Supplier",
        "th_invoice_no": "Invoice No.",
        "th_medicine": "Medicine",
        "th_qty": "Qty.",
        "th_unit": "Unit",
        "th_unit_price": "Unit price",
        "th_total_amount": "Total amount",
        "th_unit_cost": "Cost/unit",
        "th_pdf_status": "PDF Status",
        "page_info": "Page {current} of {total}",
        "btn_prev": "‹ Previous",
        "btn_next": "Next ›",

        # Detail Panel
        "detail_title": "Selected Record Detail",
        "detail_med": "Medicine",
        "detail_provider": "Supplier",
        "detail_date": "Invoice date",
        "detail_doc": "Invoice No.",
        "detail_qty": "Quantity",
        "detail_unit_price": "Unit price",
        "detail_total_amount": "Total amount",
        "detail_units_box": "Units/box",
        "detail_total_units": "Total units",
        "detail_unit_cost_stateless": "Cost per unit (Stateless)",
        "detail_detection_method": "Detection method",
        "detail_views_stateful": "Visualizations (Stateful)",
        "detail_source_sheet": "Source (original sheet)",
        "detail_pdf_status": "PDF Status",
        "detail_open_new_tab": "Open in new tab",
        "detail_file_label": "File: {path}",
        "detail_empty_selection": "Select a record to preview its PDF.",
        "detail_empty_no_doc": "This record has no document number; PDF cannot be searched.",
        "detail_empty_not_found": "No PDF found matching this record.",
        "detail_multiple_matches": "Multiple possible matches found. Select the correct one to preview:",
        "views_badge": "👁 {count} view(s)",

        # Inconsistencies
        "incons_title": "Inconsistency report",
        "incons_hint": "Click on an indicator to filter the table with those records.",
        "inc_duplicate_rows": "Duplicate rows",
        "inc_medicines_no_cost": "Medicines without cost",
        "inc_invalid_dates": "Empty or invalid dates",
        "inc_empty_docs": "Without document number",
        "inc_missing_pdfs": "Missing PDF files",
        "inc_multiple_matches": "With multiple possible matches",

        # Regex Form
        "regex_form_title": "Document and Invoice Validation with Regular Expressions (Regex)",
        "regex_form_sub": "Syntactic and business rule verification across client and server layers using formal Regex patterns.",
        "regex_field_invoice": "Invoice Number (Series-Number)",
        "regex_field_ruc": "Supplier RUC (11 digits)",
        "regex_field_sanitary": "Pharmaceutical Sanitary Registration",
        "regex_field_date": "Issue Date (YYYY-MM-DD)",
        "regex_field_email": "Audit Email Address",
        "regex_field_amount": "Total Amount ($)",
        "regex_field_pdf": "Attached PDF File Name",
        "regex_btn_validate": "Validate on Server (Business Layer)",
        "regex_btn_fill_valid": "Load Valid Example",
        "regex_btn_fill_invalid": "Load Example with Errors",
        "regex_success_alert": "Form successfully validated! All fields strictly comply with Regular Expressions.",
        "regex_error_alert": "Validation errors found. Please correct the fields highlighted in red.",
        "regex_pattern_badge": "Pattern:",
        "regex_valid_tag": "Valid",
        "regex_invalid_tag": "Invalid",

        # External Service & Component Diagram
        "btn_toggle_external_service": "🌐 External Service (FX)",
        "btn_view_component_diagram": "📐 Component Diagram",
        "ext_service_title": "Real-Time External Service Consumption (ExchangeRate-API & OpenFDA)",
        "ext_service_sub": "Direct asynchronous browser consumption (REST fetch) without going through Flask server.",
        "ext_ticker_label": "Live Exchange Rate:",
        "ext_currency_label": "Table Currency:",
        "ext_status_online": "🟢 200 OK — Live from browser",
        "ext_btn_refresh": "🔄 Refresh Rates",
        "ext_calc_title": "Live Currency Conversion Calculator",
        "ext_fda_lookup_btn": "🔍 Lookup Drug on OpenFDA",
        "ext_json_viewer_title": "JSON Payload received directly from external service:",
        "modal_diagram_title": "UML Component Diagram (UML 2.5) — Layered Architecture"
    },
    "pt": {
        # General / Header
        "app_title": "Painel de Faturas e Custos de Medicamentos",
        "loading_data": "Carregando dados da Camada de Negócios...",
        "source_label": "Fonte: {source} — folha \"{sheet}\" — gerado {generated}",
        "tier_badge": "Arquitetura em Camadas (4-Tier)",
        "view_functions_btn": "★ Ver Funções Stateful / Stateless",
        "btn_toggle_regex_form": "📋 Formulário de Validação Regex",
        "logout_btn": "Sair",
        "login_title": "Entrar — Painel GS (N-Layer)",
        "login_heading": "Painel de Faturas e Custos GS",
        "login_sub": "Tecnologias de Construção de Software",
        "username_label": "Usuário",
        "password_label": "Senha",
        "login_submit": "Entrar",
        "login_error": "Usuário ou senha incorretos.",
        "lang_selector_label": "Idioma",

        # Metrics Cards
        "card_total_records": "Registros analisados",
        "card_distinct_meds": "Medicamentos distintos",
        "card_pdfs_found": "PDFs encontrados",
        "card_pdfs_missing": "PDFs ausentes",
        "card_possible_matches": "Possíveis correspondências",
        "card_no_doc_number": "Registros sem nº de documento",
        "card_pct_linked": "% vinculados a um PDF",

        # Filters
        "filter_title": "Buscar medicamento",
        "filter_query_label": "Nome, parte do nome, princípio ativo ou concentração",
        "filter_query_placeholder": "Ex: paracetamol, amoxicilina 500, cardivas 12.5...",
        "filter_date_from": "Data de início",
        "filter_date_to": "Data final",
        "filter_provider": "Fornecedor",
        "filter_all": "Todos",
        "filter_pdf_status": "Status do PDF",
        "filter_status_found": "PDF encontrado",
        "filter_status_missing": "PDF não encontrado",
        "filter_status_possible": "Possível correspondência",
        "filter_status_empty": "Sem número de documento",
        "filter_doc_number": "Número da fatura",
        "filter_doc_placeholder": "Ex: F002-00012780",
        "filter_pdf_file": "Nome do arquivo PDF",
        "filter_pdf_placeholder": "Ex: F002-00012780 08.06.pdf",
        "btn_search": "Buscar",
        "btn_clear": "Limpar filtros",
        "btn_only_issues": "Ver apenas registros com problemas de PDF",
        "history_title": "Histórico recente de busca (Estado de Sessão - Stateful):",
        "fuzzy_title": "Você quis dizer? (Sugestões calculadas - Stateless):",
        "fuzzy_empty": "Nenhuma correspondência exata ou variação próxima encontrada para \"{query}\".",

        # Table
        "results_title": "Resultados",
        "results_found": "{count} registro(s) encontrado(s)",
        "filter_active_issue": " — filtro de inconsistência ativo",
        "th_date": "Data",
        "th_provider": "Fornecedor",
        "th_invoice_no": "Nº fatura",
        "th_medicine": "Medicamento",
        "th_qty": "Qtd.",
        "th_unit": "Unid.",
        "th_unit_price": "Preço unit.",
        "th_total_amount": "Valor total",
        "th_unit_cost": "Custo/unid.",
        "th_pdf_status": "Status PDF",
        "page_info": "Página {current} de {total}",
        "btn_prev": "‹ Anterior",
        "btn_next": "Próximo ›",

        # Detail Panel
        "detail_title": "Detalhes do registro selecionado",
        "detail_med": "Medicamento",
        "detail_provider": "Fornecedor",
        "detail_date": "Data da fatura",
        "detail_doc": "Nº fatura",
        "detail_qty": "Quantidade",
        "detail_unit_price": "Preço unitário",
        "detail_total_amount": "Valor total",
        "detail_units_box": "Unidades/caixa",
        "detail_total_units": "Unidades totais",
        "detail_unit_cost_stateless": "Custo por unidade (Stateless)",
        "detail_detection_method": "Método de detecção",
        "detail_views_stateful": "Visualizações (Stateful)",
        "detail_source_sheet": "Fonte (planilha original)",
        "detail_pdf_status": "Status PDF",
        "detail_open_new_tab": "Abrir em nova guia",
        "detail_file_label": "Arquivo: {path}",
        "detail_empty_selection": "Selecione um registro para visualizar o PDF.",
        "detail_empty_no_doc": "Este registro não tem número de documento; não é possível buscar o PDF.",
        "detail_empty_not_found": "Nenhum PDF correspondente a este registro foi encontrado.",
        "detail_multiple_matches": "Múltiplas correspondências possíveis encontradas. Selecione a correta:",
        "views_badge": "👁 {count} visualização(ões)",

        # Inconsistencies
        "incons_title": "Relatório de inconsistências",
        "incons_hint": "Clique em um indicador para filtrar a tabela com esses registros.",
        "inc_duplicate_rows": "Linhas duplicadas",
        "inc_medicines_no_cost": "Medicamentos sem custo",
        "inc_invalid_dates": "Datas vazias ou inválidas",
        "inc_empty_docs": "Sem número de documento",
        "inc_missing_pdfs": "Arquivos PDF ausentes",
        "inc_multiple_matches": "Com mais de uma possível correspondência",

        # Regex Form
        "regex_form_title": "Validação de Documentos e Faturas com Expressões Regulares (Regex)",
        "regex_form_sub": "Verificação sintática e de regras de negócio nas camadas cliente e servidor usando Regex formal.",
        "regex_field_invoice": "Número da Fatura (Série-Número)",
        "regex_field_ruc": "CNPJ/RUC do Fornecedor (11 dígitos)",
        "regex_field_sanitary": "Registro Sanitário Farmacêutico",
        "regex_field_date": "Data de Emissão (AAAA-MM-DD)",
        "regex_field_email": "E-mail de Auditoria",
        "regex_field_amount": "Valor Total",
        "regex_field_pdf": "Nome do Arquivo PDF Anexo",
        "regex_btn_validate": "Validar no Servidor (Camada de Negócios)",
        "regex_btn_fill_valid": "Carregar Exemplo Válido",
        "regex_btn_fill_invalid": "Carregar Exemplo com Erros",
        "regex_success_alert": "Formulário validado com sucesso! Todos os campos cumprem as Expressões Regulares.",
        "regex_error_alert": "Erros de validação encontrados. Corrija os campos destacados em vermelho.",
        "regex_pattern_badge": "Padrão:",
        "regex_valid_tag": "Válido",
        "regex_invalid_tag": "Inválido",

        # External Service & Component Diagram
        "btn_toggle_external_service": "🌐 Serviço Externo (Câmbio)",
        "btn_view_component_diagram": "📐 Diagrama de Componentes",
        "ext_service_title": "Consumo de Serviço Externo em Tempo Real (ExchangeRate-API & OpenFDA)",
        "ext_service_sub": "Consumo assíncrono direto do navegador (fetch REST) sem passar pelo servidor Flask.",
        "ext_ticker_label": "Taxa de Câmbio ao Vivo:",
        "ext_currency_label": "Moeda na Tabela:",
        "ext_status_online": "🟢 200 OK — Ao vivo do navegador",
        "ext_btn_refresh": "🔄 Atualizar Taxas",
        "ext_calc_title": "Calculadora de Conversão de Moeda ao Vivo",
        "ext_fda_lookup_btn": "🔍 Consultar Medicamento na OpenFDA",
        "ext_json_viewer_title": "Payload JSON recebido diretamente do serviço externo:",
        "modal_diagram_title": "Diagrama de Componentes UML (UML 2.5) — Arquitetura em Camadas"
    }
}


class I18nService:
    """Servicio de negocio para internacionalización."""

    DEFAULT_LANG = "es"
    SUPPORTED_LANGUAGES = [
        {"code": "es", "name": "Español", "flag": "🇪🇸"},
        {"code": "en", "name": "English", "flag": "🇺🇸"},
        {"code": "pt", "name": "Português", "flag": "🇧🇷"},
    ]

    def __init__(self, default_lang: str = "es"):
        self.default_lang = default_lang if default_lang in TRANSLATIONS else self.DEFAULT_LANG

    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Retorna lista de idiomas soportados con código, nombre y bandera."""
        return self.SUPPORTED_LANGUAGES

    def is_supported(self, lang: Optional[str]) -> bool:
        """Verifica si un código de idioma está soportado."""
        return lang in TRANSLATIONS if lang else False

    def translate(self, key: str, lang: Optional[str] = None, **kwargs) -> str:
        """
        Retorna la traducción correspondiente a la clave `key`.
        Aplica fallback jerárquico: idioma solicitado -> idioma por defecto -> clave original.
        """
        target_lang = lang if lang and lang in TRANSLATIONS else self.default_lang
        text = TRANSLATIONS.get(target_lang, {}).get(key)
        
        # Fallback a idioma por defecto
        if text is None:
            text = TRANSLATIONS.get(self.default_lang, {}).get(key, key)

        # Formatear parámetros dinámicos si existen
        if kwargs and isinstance(text, str):
            try:
                return text.format(**kwargs)
            except Exception:
                return text

        return text

    def get_translations_bundle(self, lang: Optional[str] = None) -> Dict[str, str]:
        """Obtiene todo el catálogo de traducciones para enviar al cliente JavaScript."""
        target_lang = lang if lang and lang in TRANSLATIONS else self.default_lang
        bundle = dict(TRANSLATIONS.get(self.default_lang, {}))
        bundle.update(TRANSLATIONS.get(target_lang, {}))
        return bundle
