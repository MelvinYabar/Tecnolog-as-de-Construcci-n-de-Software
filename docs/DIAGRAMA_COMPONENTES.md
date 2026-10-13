# Diagrama de Componentes UML — Dashboard de Auditoría y Costos GS
## Arquitectura en Capas (N-Layer / Multi-Tier) y Servicios Externos

**Curso:** Tecnologías de Construcción de Software  
**Estándar:** UML 2.5 — Diagrama de Componentes (Component Diagram)  
**Propósito:** Modelar la descomposición modular del sistema, los componentes autónomos de software (`<<component>>`), sus interfaces provistas y requeridas, y las dependencias físicas y lógicas entre capas y servicios externos.

---

## 1. Diagrama de Componentes UML

```mermaid
flowchart TD
    %% =========================================================================
    %% SERVICIOS EXTERNOS (EXTERNAL SERVICES)
    %% =========================================================================
    subgraph ExternalServices ["<<external system>>\nServicios Externos en la Nube"]
        ExtExchange["<<service>>\nExchangeRate-API\n(open.er-api.com)\n[Servicio REST de Tasas de Cambio]"]
        ExtFDA["<<service>>\nOpenFDA Drug API\n(api.fda.gov)\n[Servicio REST Farmacológico EE.UU.]"]
    end

    %% =========================================================================
    %% CAPA 1: PRESENTACIÓN (PRESENTATION TIER)
    %% =========================================================================
    subgraph PresentationTier ["1. Capa de Presentación (Presentation Tier)"]
        subgraph ClientBrowser ["<<execution environment>> Navegador Web (Client-Side JS & UI)"]
            DashboardUI["<<component>>\nDashboardView\n(index.html / Jinja2)"]
            AppCtrl["<<component>>\nAppController\n(app.js)\n[Filtros, Tabla, Paginación, Fuzzy]"]
            RegexCtrl["<<component>>\nRegexValidatorController\n(regex-validator.js)\n[Validación Live Regex]"]
            ExtCtrl["<<component>>\nExternalServiceController\n(external-service.js)\n[Consumo Directo fetch REST]"]
        end

        subgraph ServerFlask ["<<execution environment>> Servidor Web Flask (Server-Side)"]
            InvCtrl["<<component>>\nInvoiceController\n(/api/invoices/*)"]
            AuthCtrl["<<component>>\nAuthController\n(/login, /logout)"]
            AuditCtrl["<<component>>\nAuditController\n(/api/audit/*)"]
            ViewCtrl["<<component>>\nViewController\n(/dashboard, /demo)"]
        end
    end

    %% =========================================================================
    %% CAPA 2: LÓGICA DE NEGOCIO (BUSINESS TIER)
    %% =========================================================================
    subgraph BusinessTier ["2. Capa de Lógica de Negocio (Business Tier)"]
        InvService["<<component>>\nInvoiceService\n(invoice_service.py)\n[Matching, Costos Unitarios, Historial]"]
        AuthService["<<component>>\nAuthService\n(auth_service.py)\n[Autenticación y Credenciales]"]
        AuditService["<<component>>\nAuditService\n(audit_service.py)\n[Márgenes, Precios y Semáforos]"]
        I18nService["<<component>>\nI18nService\n(i18n_service.py)\n[Traducción es/en/pt & Fallback]"]
        RegexService["<<component>>\nRegexValidatorService\n(validator_service.py)\n[Reglas Sintácticas Regex]"]
    end

    %% =========================================================================
    %% CAPA 3: ACCESO A DATOS (DATA ACCESS TIER)
    %% =========================================================================
    subgraph DataAccessTier ["3. Capa de Acceso a Datos (Data Access Tier)"]
        IInvRepo(["<<interface>>\nIInvoiceRepository"])
        IAuditRepo(["<<interface>>\nIAuditRepository"])
        IDocStorage(["<<interface>>\nIDocumentStorage"])

        ExcelRepo["<<component>>\nExcelInvoiceRepository\n(excel_invoice_repo.py)"]
        AuditRepo["<<component>>\nJsonAuditRepository\n(json_audit_repo.py)"]
        DocStorage["<<component>>\nDocumentStorage\n(document_storage.py)"]

        ExcelRepo -.->|realizes / implements| IInvRepo
        AuditRepo -.->|realizes / implements| IAuditRepo
        DocStorage -.->|realizes / implements| IDocStorage
    end

    %% =========================================================================
    %% CAPA 4: DOMINIO (DOMAIN TIER)
    %% =========================================================================
    subgraph DomainTier ["4. Capa Transversal de Dominio (Domain Core)"]
        Entities["<<entity>>\nInvoiceItem\nProductAudit\nUser"]
        DTOs["<<dto>>\nInvoiceFilterDTO\nAuditUpdateDTO"]
    end

    %% =========================================================================
    %% CAPA 5: FUENTES DE DATOS FÍSICAS (INFRASTRUCTURE / DATA SOURCES)
    %% =========================================================================
    subgraph DataSources ["5. Fuentes Físicas de Datos (Data Sources)"]
        ExcelFile[("Excel: Costo real por unidad\n(desde facturas.xlsx)")]
        PDFStorage[("Almacén de Facturas PDF\n(directorio COMPRAS/)")]
        JSONCache[("Archivos de Caché JSON\n(invoice_data.json, audit_data.json)")]
    end

    %% =========================================================================
    %% RELACIONES Y DEPENDENCIAS
    %% =========================================================================

    %% Consumo de Servicios Externos DIRECTO DESDE EL FRONTEND
    ExtCtrl ==>|HTTPS / GET JSON (fetch directo)| ExtExchange
    ExtCtrl ==>|HTTPS / GET JSON (fetch directo)| ExtFDA

    %% Interacción interna en el navegador
    DashboardUI --> AppCtrl
    DashboardUI --> RegexCtrl
    DashboardUI --> ExtCtrl
    ExtCtrl -.->|tasas de conversión| AppCtrl

    %% Comunicación Cliente -> Servidor (Presentación)
    AppCtrl -->|AJAX HTTP GET /api/invoices/data| InvCtrl
    AppCtrl -->|AJAX HTTP GET /api/invoices/search| InvCtrl
    RegexCtrl -->|AJAX HTTP POST /api/invoices/validate-form| InvCtrl
    DashboardUI -->|HTTP GET /dashboard| ViewCtrl
    DashboardUI -->|HTTP POST /login| AuthCtrl

    %% Presentación -> Negocio
    InvCtrl --> InvService
    InvCtrl --> RegexService
    AuthCtrl --> AuthService
    AuditCtrl --> AuditService
    ViewCtrl --> I18nService

    %% Negocio -> Interfaces de Acceso a Datos
    InvService --> IInvRepo
    InvService --> IDocStorage
    AuditService --> IAuditRepo

    %% Acceso a Datos -> Almacenamiento Físico
    ExcelRepo --> ExcelFile
    ExcelRepo --> JSONCache
    AuditRepo --> JSONCache
    DocStorage --> PDFStorage

    %% Dependencia común del modelo de Dominio
    PresentationTier -.-> DomainTier
    BusinessTier -.-> DomainTier
    DataAccessTier -.-> DomainTier
```

---

## 2. Descripción de Componentes por Capa

### A. Capa de Servicios Externos (External Cloud Services)
1. **`ExchangeRate-API` (`open.er-api.com`):**
   - **Tipo:** Servicio Web REST Externo (SaaS).
   - **Interfaz Provista:** `GET /v6/latest/PEN`
   - **Formato:** JSON abierto (sin clave de API requerida y habilitado para CORS).
   - **Consumo:** Consumido **exclusivamente desde el front end** mediante `window.fetch()` por el componente `ExternalServiceController`. Provee tasas de cambio en tiempo real (PEN a USD, EUR, BRL) para la conversión dinámica de costos e importes de medicamentos.
2. **`OpenFDA Drug API` (`api.fda.gov`):**
   - **Tipo:** Servicio Web REST de la Administración de Alimentos y Medicamentos de EE.UU. (FDA).
   - **Interfaz Provista:** `GET /drug/label.json?search=openfda.generic_name:...`
   - **Consumo:** Consulta farmacológica internacional en tiempo real para enriquecer medicamentos seleccionados con principios activos, advertencias y fabricante oficial.

### B. Capa de Presentación (Presentation Tier)
Organizada en dos sub-entornos:
#### Sub-entorno Cliente (Navegador Web / JavaScript ES6):
1. **`DashboardView`:** Plantilla maestra HTML5/Jinja2 ([`index.html`](../src/presentation/templates/index.html)) con diseño responsivo, paneles modulares y soporte multilingüe.
2. **`AppController` (`app.js`):** Gestiona la tabla de resultados, el motor de búsqueda en cliente, paginación, filtros avanzados y recálculo de divisas en tiempo real.
3. **`RegexValidatorController` (`regex-validator.js`):** Controlador de validación reactiva en tiempo real mediante Expresiones Regulares con detección sintáctica inmediata (`input`/`blur`).
4. **`ExternalServiceController` (`external-service.js`):** Componente dedicado a la comunicación asíncrona con las APIs externas en la nube, cálculo de latencia de red, conversión matemática y visualización del payload JSON.

#### Sub-entorno Servidor (Flask Web Server & Blueprints):
1. **`InvoiceController` (`invoice_bp`):** Expone endpoints REST para consulta de facturas (`/api/invoices/data`, `/api/invoices/search`), descarga protegida de PDFs y validación de reglas de negocio por Regex (`/api/invoices/validate-form`).
2. **`AuthController` (`auth_bp`):** Control de acceso y sesiones de usuario (`/login`, `/logout`).
3. **`AuditController` (`audit_bp`):** Endpoints para auditoría de precios y márgenes comerciales.
4. **`ViewController` (`view_bp`):** Renderizado de vistas HTML y ruteo de navegación.

### C. Capa de Lógica de Negocio (Business Logic Tier)
1. **`InvoiceService`:** Contiene los algoritmos de búsqueda difusa (Fuzzy Matching con Coeficiente de Sørensen-Dice), resolución de coincidencias con PDFs, cálculo determinista de costo por unidad (Stateless) y registro de historial en sesión (Stateful).
2. **`RegexValidatorService`:** Motor de validación sintáctica formal con patrones Regex compilados para números de factura, RUC, registros sanitarios, fechas ISO, correos y montos.
3. **`AuthService`:** Lógica de autenticación con verificación de usuarios contra credenciales del sistema.
4. **`AuditService`:** Reglas de auditoría para identificación de inconsistencias, medicamentos sin costo o fechas anómalas.
5. **`I18nService`:** Motor de internacionalización desacoplado con catálogos en Español, Inglés y Portugués, resolución de claves y fallback jerárquico.

### D. Capa de Acceso a Datos (Data Access Tier)
Implementa el patrón **Repository** desacoplado mediante interfaces abstractas en Python (`abc.ABC`):
1. **Interfaces:**
   - `IInvoiceRepository`: Contrato para consultar y persistir facturas.
   - `IAuditRepository`: Contrato para estados de auditoría de productos.
   - `IDocumentStorage`: Contrato para resolución segura de archivos físicos.
2. **Implementaciones:**
   - `ExcelInvoiceRepository`: Deserializa registros desde el archivo Excel original (`desde facturas.xlsx`) y caché JSON.
   - `JsonAuditRepository`: Persistencia de auditorías en archivo JSON estructurado.
   - `DocumentStorage`: Verificación y lectura segura de archivos PDF en la carpeta `COMPRAS/`, protegiendo contra vulnerabilidades de *Directory Traversal*.

### E. Capa de Dominio (Domain Core)
Capa transversal que define las entidades del negocio (`InvoiceItem`, `ProductAudit`, `User`) y los DTOs (`InvoiceFilterDTO`, `AuditUpdateDTO`). No tiene dependencias hacia capas externas.

---

## 3. Matriz de Interfaces Provistas y Requeridas

| Componente | Interfaces Provistas (Exposed / Provided) | Interfaces Requeridas (Consumed / Required) |
| :--- | :--- | :--- |
| **`ExternalServiceController`** | `convertCurrency()`, `fetchExchangeRates()`, `lookupDrug()` | `ExchangeRate-API`, `OpenFDA Drug API` |
| **`AppController`** | `renderTable()`, `applyFilters()`, `updateCurrency()` | `InvoiceController` (`/api/invoices/data`), `ExternalServiceController` |
| **`RegexValidatorController`** | `validateSingleField()`, `validateAll()` | `InvoiceController` (`/api/invoices/validate-form`) |
| **`InvoiceController`** | REST API (`/api/invoices/*`) | `InvoiceService`, `RegexValidatorService` |
| **`InvoiceService`** | `search_invoices()`, `calculate_unit_cost()` | `IInvoiceRepository`, `IDocumentStorage` |
| **`ExcelInvoiceRepository`** | `IInvoiceRepository` | Sistema de archivos (`ExcelFile`, `JSONCache`) |
| **`DocumentStorage`** | `IDocumentStorage` | Sistema de archivos (`COMPRAS/*.pdf`) |
