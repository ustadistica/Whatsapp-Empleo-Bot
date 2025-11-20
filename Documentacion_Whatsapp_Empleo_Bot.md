# Proyecto Integral: Extracción y Clasificación de Ofertas de Empleo desde WhatsApp

Este documento describe de manera técnica y completa el funcionamiento del proyecto **Whatsapp-Empleo-Bot**, cuyo propósito es:

1. Extraer información de canales de WhatsApp que publican ofertas laborales.
2. Guardar los mensajes en una base de datos o CSV.
3. Transformar los mensajes en una estructura uniforme en JSON.
4. Clasificar las ofertas mediante modelos de IA (OpenAI/GPT y Gemini).
5. Enriquecer cada oferta con categorías laborales y códigos CUOC de Colombia.
6. Generar archivos listos para análisis posteriores.

El proyecto se implementó en Python y utiliza Selenium, SQLite, Pandas y modelos de lenguaje avanzados.

---

# 1. Arquitectura General del Proyecto

El sistema completo consta de 4 módulos principales:

```
src/
│── scraping/
│   ├── whatsapp_scraper.py        ← Web scraping con Selenium
│   └── exportar_db.py             ← Exportación CSV desde SQLite
│
├── processing/
│   ├── limpiar_mensajes.py        ← Limpieza y normalización
│   └── construir_estructura.py    ← Conversión a JSON
│
├── ofertas/
│   ├── clasificar_ofertas.py      ← Clasificador con IA + CUOC
│   └── CUOC-indice-2024.xlsx      ← Clasificación ocupacional
│
├── data/
│   ├── whatsapp.db                ← Base de datos SQLite
│   ├── mensajes.csv               ← Exportación simple
│   └── ofertas.json               ← Archivo estructurado
```

Cada módulo es independiente y puede ejecutarse por separado.

---

# 2. Web Scraping desde WhatsApp Web

## 2.1. Tecnologías utilizadas
- **Selenium + ChromeDriver**
- **Webdriver Manager**
- **XPath dinámicos**
- **Control de scroll para cargar mensajes antiguos**
- **SQLite como base de datos persistente**

## 2.2. Flujo de scraping

1. Abrir WhatsApp Web.
2. Detectar automáticamente el botón “Canales”.
3. Buscar el artículo categorizado en `nombre_canal`.
4. Realizar scroll hacia arriba para cargar mensajes antiguos.
5. Extraer:
   - Remitente
   - Texto del mensaje
   - Fecha y hora del mensaje (si WhatsApp lo muestra)
6. Filtrar mensajes que solo contienen emojis.
7. Guardarlos en SQLite.

### Ejemplo de estructura en SQLite

| id | remitente | contenido | fecha_hora |
|----|-----------|-----------|------------|
| 1  | Empleo Bogotá | *Vacante para analista…* | 2025-09-16 17:18:12 |

Con esto se crea la base de datos inicial para el procesamiento posterior.

---

# 3. Exportación del Dataset

El proyecto incluye un script para exportar:

- archivos CSV (`mensajes.csv`)
- respaldos de la base de datos (`whatsapp.db`)
- JSON estructurados

Formato CSV:

```
id, remitente, contenido, fecha_hora
51, Empleo en Bogotá, Vacante para…, 2025-09-16 21:56:04
```

---

# 4. Procesamiento y Limpieza de Datos

Una vez extraídos los mensajes, deben limpiarse:

### Etapas:

1. Normalización de saltos de línea.
2. Eliminación de duplicados.
3. Filtrado de mensajes irrelevantes o vacíos.
4. Limpieza de emojis y caracteres no útiles.
5. Reconstrucción del texto final para análisis.

El objetivo es dejar únicamente el contenido útil de cada publicación laboral.

---

# 5. Construcción del Archivo JSON de Ofertas

Todos los mensajes limpios se convierten en un JSON estructurado:

```json
{
  "ofertas_detalladas": [
    {
      "contenido": "Vacante para director de mercadeo...",
      "cargo": "",
      "nivel_educativo": "",
      "tipo_contrato": "",
      "experiencia": "",
      "ubicacion": "",
      "salario": "",
      "contenido_limpio": "Vacante para director..."
    }
  ]
}
```

Este archivo **sirve como entrada para los clasificadores de IA**.

---

# 6. Clasificador de Ofertas con Inteligencia Artificial

El sistema permite usar **dos motores de IA**:

## 6.1. Uso de OpenAI (GPT)

Inicialmente se utilizó:

```python
from openai import OpenAI
client = OpenAI(api_key=...)
```

Sin embargo, OpenAI detectó la API Key en GitHub y bloqueó los push.  
Además, requiere créditos pagos, lo que impidió escalar el análisis.

Por ello, se migró a un clasificador **100% gratuito** con **Gemini**.

---

# 7. Clasificador con Gemini (Google AI)

## 7.1. Librería utilizada

```python
from google import genai
client = genai.Client(api_key=...)
```

## 7.2. Ventajas

- Llamadas gratuitas.
- Modelos actualizados como `gemini-2.5-flash`.
- Soporte para clasificación estructurada.
- Buen rendimiento en español.

## 7.3. Prompt utilizado

El modelo recibe:

- Texto completo de la oferta.
- Metadatos extraídos.
- Lista de categorías laborales.
- Fragmento de la Clasificación Ocupacional Colombiana (CUOC).

Y devuelve un JSON:

```json
{
  "categoria": "Tecnología/Ingeniería",
  "subcategoria": "Desarrollo de Software",
  "confianza": 0.94,
  "cuoc_codigo": "2151",
  "cuoc_titulo": "Ingeniero(a) en Desarrollo de Software"
}
```

## 7.4. Manejo de errores

Incluye manejo de:

- Respuestas corruptas  
- Bloques Markdown ```json  
- Errores 503 (modelo saturado)  
- JSON inválido  
- Llamadas máximas configurables con `MAX_LLM_CALLS`

---

# 8. Integración con CUOC (Clasificación Colombiana de Ocupaciones)

El archivo:

```
CUOC-indice-2024.xlsx
```

Se utiliza para:

- Dar contexto al modelo Gemini.
- Sugerir códigos ocupacionales probables.

Si CUOC no está disponible o no carga correctamente:

```
CUOC cargado pero sin filas utilizables
```

El sistema continúa sin afectar el procesamiento.

---

# 9. Limitaciones Identificadas

1. WhatsApp Web cambia frecuentemente sus selectores → el scraper puede requerir mantenimiento.
2. OpenAI requiere créditos y además GitHub bloquea la API Key.
3. Gemini puede devolver respuestas en formato Markdown que deben limpiarse.
4. WhatsApp no muestra siempre la fecha del mensaje → muchos registros deben asumir la fecha de extracción.
5. CUOC no siempre coincide perfectamente con mensajes informales.

---

# 10. Mejoras Futuras Propuestas

- Implementar un clasificador local (HuggingFace) sin necesidad de API.
- Automatizar el scraping en un servidor con Chrome Headless.
- Utilizar embeddings para enriquecer la clasificación.
- Desplegar un dashboard (Power BI / Streamlit / Superset).
- Entrenar un modelo propio con las clasificaciones generadas.

---

# 11. Conclusión

Este proyecto integra múltiples tecnologías para resolver un problema real:

- **Extracción automática** de contenido laboral desde WhatsApp.
- **Procesamiento inteligente** de textos.
- **Clasificación profesional** con IA y CUOC.
- **Estructura empresarial** del repositorio.
- **Automatización completa**, de la adquisición al análisis.

Es un pipeline robusto, escalable y listo para integrarse con analítica avanzada o sistemas de información.

---

