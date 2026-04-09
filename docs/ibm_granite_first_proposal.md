# Propuesta para IBM — Arquitectura Granite-First para `tbcoin-engine-ml`

## Resumen ejecutivo

Solicitamos apoyo para convertir `tbcoin-engine-ml` en una arquitectura **Granite-First** desplegada sobre **IBM Cloud** y **watsonx.ai**, manteniendo una base modular, portable y alineada con un enfoque de **soberanía técnica**.

El proyecto actual combina:

- API backend en **FastAPI** para operaciones de moneda, transacciones y acciones ML.
- Servicios auxiliares para **agentes autónomos**, entrenamiento ML y procesamiento batch.
- Persistencia con **PostgreSQL** y **Redis**.
- Trazabilidad de modelos con **MLflow** y almacenamiento de artefactos tipo S3.
- Despliegue containerizado con una orientación previa a **IBM Code Engine**.

La meta es rediseñar el proyecto para que los componentes de inferencia y orquestación se apoyen únicamente en la familia **Granite**, usando:

- `ibm/granite-3.0-8b-instruct` para agentes rápidos, clasificación y orquestación.
- `ibm/granite-13b-instruct-v2` para razonamiento complejo, síntesis y RAG.
- **watsonx.ai** como plano principal de inferencia y despliegue.

---

## Contexto técnico del proyecto actual

### Componentes detectados

1. **API principal**
   - Implementada con FastAPI.
   - Endpoints para salud, monedas, transacciones y acciones ML.
   - Configuración basada en `.env`.

2. **Agente autónomo**
   - Servicio separado para análisis continuo y lógica de decisión.
   - Puede evolucionar hacia un patrón multiagente orquestado con Granite.

3. **ML worker**
   - Ejecuta entrenamiento, procesos batch y tareas de soporte ML.
   - Actualmente acoplado a almacenamiento local de modelos y MLflow.

4. **Persistencia**
   - PostgreSQL para datos transaccionales/estructurados.
   - Redis para cache, colas ligeras y coordinación rápida.

5. **Artefactos y tracking**
   - MLflow para experimentación.
   - MinIO local como almacenamiento compatible S3.
   - Ya existe interés en migrar estos artefactos a **IBM Cloud Object Storage (COS)**.

6. **Despliegue cloud**
   - Scripts y manifiestos para **IBM Code Engine**.
   - Separación natural entre API, worker ML y listener batch.

---

## Mapeo propuesto a servicios IBM Cloud

| Componente actual | Servicio IBM Cloud propuesto | Motivo |
|---|---|---|
| FastAPI API | **IBM Code Engine App** | Escalado serverless de contenedores HTTP |
| Agente autónomo / orquestador | **watsonx.ai + Code Engine** | Orquestación con Granite y herramientas externas |
| Worker ML / batch | **IBM Code Engine Job** | Ejecución bajo demanda o programada |
| PostgreSQL | **Databases for PostgreSQL** | Persistencia relacional gestionada |
| Redis | **Databases for Redis** | Cache y coordinación con baja latencia |
| MinIO / artefactos S3 | **Cloud Object Storage (COS)** | Artefactos de modelos, datasets y prompts versionados |
| MLflow tracking | **MLflow sobre Code Engine + COS** o sustitución parcial por watsonx.ai assets | Trazabilidad y centralización |
| Inferencia LLM | **watsonx.ai** | Uso administrado de Granite con gobierno y despliegue |
| Observabilidad | **IBM Cloud Monitoring / Log Analysis** | Métricas, logs y alertas operativas |

---

## Arquitectura Granite-First propuesta

### 1. Plano de orquestación rápida

Usar **Granite 3.0 8B Instruct** para:

- routing de tareas,
- clasificación de intención,
- selección de herramientas,
- formateo estructurado de salidas,
- decisión rápida en flujos agentic.

### 2. Plano de razonamiento profundo

Usar **Granite 13B Instruct v2** para:

- análisis compuesto multi-paso,
- consolidación de señales del mercado,
- síntesis financiera,
- respuestas RAG sobre documentos internos, trazas operativas y datos de activos.

### 3. Capa RAG

Fuentes iniciales sugeridas:

- documentación del repositorio,
- métricas y reportes generados,
- artefactos de entrenamiento,
- snapshots transaccionales y señales on-chain procesadas,
- políticas y configuraciones de despliegue.

Persistencia sugerida:

- documentos y artefactos en **COS**,
- metadatos en **PostgreSQL**,
- cache de resultados intermedios en **Redis**.

### 4. Despliegue

- **Code Engine App** para la API pública.
- **Code Engine App o Job** para el orquestador agentic.
- **Code Engine Job** para entrenamiento y pipelines batch.
- **watsonx.ai** para inferencia y AI service.

---

## Solicitud específica a IBM

Solicitamos validación y guía para una réplica de referencia con estas características:

1. **Arquitectura Granite-First** para este proyecto.
2. **Patrón de despliegue recomendado** entre Code Engine y watsonx.ai.
3. **Ruta soportada en free tier / bajo costo** para PoC.
4. **Buenas prácticas** para:
   - inferencia con Granite,
   - versionado de prompts,
   - RAG con COS,
   - despliegue como AI Service,
   - observabilidad y gobierno.

---

## Prompt técnico para IBM / watsonx.ai

```text
# ROL
Eres un Arquitecto de Soluciones Senior especializado en IBM Cloud, watsonx.ai y modelos Granite. Analiza el proyecto `tbcoin-engine-ml` y propón una arquitectura Granite-First modular, portable y escalable.

# OBJETIVO TÉCNICO
Convertir el proyecto a una arquitectura que use exclusivamente modelos Granite:
- Granite-3.0-8b-instruct para agentes rápidos y orquestación.
- Granite-13b-instruct-v2 para razonamiento complejo y RAG.
- watsonx.ai para inferencia y despliegue como AI Service.

# STACK DE RÉPLICA REQUERIDO
Genera ejemplos usando:
- ibm-watsonx-ai
- langchain-ibm
- ibm-cos-sdk
- langgraph
- pydantic

# CONTEXTO DEL PROYECTO
El proyecto incluye:
- API FastAPI para health, coins, transactions y ML actions.
- servicios de agente autónomo,
- worker ML,
- PostgreSQL,
- Redis,
- tracking de modelos,
- artefactos tipo S3,
- despliegue orientado a IBM Code Engine.

# TAREAS
1. Analiza componentes, APIs, bases de datos y flujos.
2. Mapea cada componente a servicios IBM Cloud.
3. Diseña una réplica Granite-First con patrón agentic + RAG.
4. Propón el despliegue como AI Service en watsonx.ai.
5. Incluye consideraciones de free tier / PoC económica.

# RESTRICCIONES
- Usa solo modelos de la familia Granite.
- Mantén el código modular y ejecutable.
- Usa placeholders para secretos.
```

---

## Ejemplo de réplica en Python

```python
import os
from typing import List

from pydantic import BaseModel, Field
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams


class ProjectComponent(BaseModel):
    name: str
    purpose: str
    ibm_service: str


class ArchitectureRequest(BaseModel):
    project_name: str = "tbcoin-engine-ml"
    components: List[ProjectComponent]
    constraints: List[str] = Field(default_factory=list)


credentials = {
    "url": os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
    "apikey": os.getenv("IBM_CLOUD_API_KEY", "YOUR_IBM_CLOUD_API_KEY"),
}

project_id = os.getenv("WATSONX_PROJECT_ID", "YOUR_PROJECT_ID")

reasoning_params = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.MAX_NEW_TOKENS: 500,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.TEMPERATURE: 0.0,
}

orchestrator_params = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.MAX_NEW_TOKENS: 160,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.TEMPERATURE: 0.0,
}


granite_reasoner = Model(
    model_id="ibm/granite-13b-instruct-v2",
    params=reasoning_params,
    credentials=credentials,
    project_id=project_id,
)

granite_orchestrator = Model(
    model_id="ibm/granite-3-8b-instruct",
    params=orchestrator_params,
    credentials=credentials,
    project_id=project_id,
)


def build_prompt(request: ArchitectureRequest) -> str:
    component_lines = "\n".join(
        f"- {c.name}: {c.purpose} -> {c.ibm_service}" for c in request.components
    )
    constraints = "\n".join(f"- {c}" for c in request.constraints) or "- Solo modelos Granite"

    return f"""
Analiza el siguiente proyecto y genera una propuesta Granite-First para IBM Cloud.

Proyecto: {request.project_name}

Componentes detectados:
{component_lines}

Restricciones:
{constraints}

Devuelve:
1. Arquitectura IBM Cloud recomendada.
2. Separación entre Granite 8B y Granite 13B.
3. Patrón RAG sugerido.
4. Ruta de despliegue como AI Service en watsonx.ai.
5. Recomendaciones para una PoC low-cost.
""".strip()


def replica_analyser(request: ArchitectureRequest) -> str:
    routing_prompt = (
        "Clasifica este proyecto y resume en 5 líneas qué componentes deben ser "
        "orquestados por Granite-3.0-8b-instruct.\n\n"
        + build_prompt(request)
    )
    routing_summary = granite_orchestrator.generate_text(prompt=routing_prompt)

    reasoning_prompt = (
        "Usa esta preclasificación para producir la arquitectura final.\n\n"
        f"Preclasificación:\n{routing_summary}\n\n"
        + build_prompt(request)
    )
    return granite_reasoner.generate_text(prompt=reasoning_prompt)


if __name__ == "__main__":
    request = ArchitectureRequest(
        components=[
            ProjectComponent(name="FastAPI API", purpose="servicio HTTP principal", ibm_service="Code Engine App"),
            ProjectComponent(name="ML Worker", purpose="entrenamiento y batch", ibm_service="Code Engine Job"),
            ProjectComponent(name="PostgreSQL", purpose="persistencia transaccional", ibm_service="Databases for PostgreSQL"),
            ProjectComponent(name="Redis", purpose="cache y coordinación", ibm_service="Databases for Redis"),
            ProjectComponent(name="Model artifacts", purpose="datasets, prompts y modelos", ibm_service="Cloud Object Storage"),
            ProjectComponent(name="LLM inference", purpose="orquestación y razonamiento", ibm_service="watsonx.ai"),
        ],
        constraints=[
            "Usar solo modelos Granite",
            "Priorizar modularidad y portabilidad",
            "Diseñar una PoC apta para free tier o coste mínimo",
        ],
    )

    print(replica_analyser(request))
```

---

## Agente básico de búsqueda / RAG (estructura recomendada)

### Diseño sugerido

1. **Ingesta**
   - documentos, reportes y artefactos a COS.
2. **Indexación**
   - metadatos y referencias en PostgreSQL.
3. **Orquestación**
   - Granite 8B decide si responder directo o activar recuperación.
4. **Recuperación**
   - consulta de documentos y contexto relevante.
5. **Síntesis final**
   - Granite 13B construye la respuesta fundamentada.

---

## Proceso de despliegue como AI Service en watsonx.ai

### Fase 1 — Preparación

- Crear proyecto en watsonx.ai.
- Registrar credenciales y `project_id` vía variables de entorno.
- Subir artefactos auxiliares a COS.

### Fase 2 — Empaquetado

- Empaquetar la lógica agentic en un servicio Python reproducible.
- Separar:
  - configuración,
  - herramientas,
  - acceso a COS,
  - capa RAG,
  - invocación Granite.

### Fase 3 — Serving

- Exponer la lógica como **AI Service** en watsonx.ai cuando el patrón de serving lo permita.
- Mantener procesos batch y auxiliares en **Code Engine Jobs**.
- Reservar la API pública para tráfico de aplicación en **Code Engine App**.

### Fase 4 — Observabilidad

- logs estructurados,
- métricas de latencia por modelo,
- trazabilidad de prompts,
- versionado de artefactos y datasets.

---

## Variante de PoC para free tier / costo mínimo

Para una prueba de concepto inicial:

1. **Code Engine App** para la API principal.
2. **Code Engine Job** para entrenamiento puntual o ingesta batch.
3. **COS** para artefactos.
4. **Databases for PostgreSQL** o base relacional mínima según disponibilidad/coste.
5. **Databases for Redis** solo si el patrón de coordinación lo exige realmente.
6. **watsonx.ai** con invocaciones controladas y límites de tokens para reducir costo.

Recomendación práctica:

- Granite 8B para la mayoría del routing.
- Granite 13B solo en pasos de razonamiento de alto valor.
- cache de resultados y reducción de contexto antes de invocar el modelo grande.

---

## Mensaje corto para enviar a IBM

```text
Hola equipo IBM,

Estamos evaluando la migración del proyecto `tbcoin-engine-ml` a una arquitectura Granite-First sobre IBM Cloud. El sistema actual combina FastAPI, agentes autónomos, workers ML, PostgreSQL, Redis, tracking de modelos y almacenamiento de artefactos tipo S3, con una orientación de despliegue hacia IBM Code Engine.

Nos gustaría validar una arquitectura de referencia que use exclusivamente:
- Granite-3.0-8b-instruct para orquestación y agentes rápidos.
- Granite-13b-instruct-v2 para razonamiento complejo y RAG.
- watsonx.ai para inferencia y despliegue como AI Service.
- IBM Cloud Object Storage para artefactos y datasets.
- Databases for PostgreSQL / Redis para persistencia y coordinación.

Adjuntamos una propuesta técnica con mapeo de componentes, diseño target y ejemplo Python de réplica. Agradeceríamos recomendaciones para una PoC de bajo costo / free tier, así como mejores prácticas para despliegue, observabilidad y gobierno en watsonx.ai.

Gracias.
```

---

## Terraform adjunto

También se incluye un scaffold Terraform alineado con esta propuesta en:

- `infrastructure/terraform/ibm-granite-first/`

Este bloque provisiona la capa base de infraestructura para IBM Cloud:

- Resource Group
- Cloud Object Storage + bucket de artefactos
- Databases for PostgreSQL
- Databases for Redis
- Code Engine Project
- opción de runtime/service instance para watsonx.ai

La capa de despliegue de aplicaciones sigue apoyándose en los manifiestos y scripts ya existentes del repositorio para Code Engine.
