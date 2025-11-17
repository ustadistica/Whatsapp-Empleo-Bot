# Proyecto: Análisis de Ofertas Laborales de Canales WhatsApp en Colombia 
 
---
![Logo Universidad Santo Tomás](https://usantotomas.edu.co/hs-fs/hubfs/social-suggested-images/usantotomas.edu.cohs-fshubfsLogo%20Santoto%20-%20SP%20Bogota%20Horizontal%20blanco-2.png)

## Consultorio de Estadística y Ciencia de Datos
*Universidad Santo Tomás*

Responsables

- Josue Pedraza 
- Natalia Zárate
- Paula Guevara 

----------------------------------------------

## Introducción

El proyecto tiene como objetivo analizar ofertas laborales publicadas en canales de WhatsApp en Colombia, una fuente informal pero cada vez más utilizada para la búsqueda de empleo. Debido a que estas ofertas suelen ser desestructuradas, incompletas y altamente heterogéneas, se requiere un proceso sistemático de recolección, limpieza y análisis para convertirlas en información útil sobre el mercado laboral colombiano.

Para ello se desarrolló un pipeline en Python que realiza *web scraping, normalización del texto y  clasificación automática de las ofertas* usando dos enfoques complementarios:

1. *Reglas basadas en palabras clave*
2. *Modelos de lenguaje (IA) para clasificación ocupacional*
   incluyendo categorías propias y referencias a la *Clasificación Nacional de Ocupaciones (CNO/CUOC)* de Colombia.

El resultado es una base de datos estructurada que permite estudiar sectores económicos, perfiles laborales patrones del mercado laboral que circula en canales alternativos de difusión.

---

## Descripción General

Este repositorio documenta la primera fase del proyecto, cuyo propósito es *construir y depurar una base de datos de ofertas laborales* extraídas de un canal de WhatsApp y clasificarlas de manera sistemática.

Las fases realizadas incluyen:

* Extracción de datos mediante *web scraping de WhatsApp Web*.
* Limpieza y normalización de textos.
* Identificación automática de categorías laborales (Call center, Logística, Salud, Tecnología, etc.).
* *Clasificación ocupacional preliminar* según categorías del *CNO/CUOC*.
* Integración de la información en un archivo estructurado (analisis_ofertas_empleo_clasificado.json).

El objetivo final es crear un insumo que permita análisis exploratorios, construcción de dashboards, y fases posteriores de *modelamiento con IA* para predicción, extracción semántica avanzada o detección de tendencias laborales.



### ¿Cómo son los datos originales en WhatsApp?

Los mensajes del canal presentan problemas comunes:

* Texto no estructurado.
* Ortografía inconsistente.
* Información fragmentada o repetida.
* Emojis y caracteres no útiles.
* Ausencia de formato estándar de cargo, salario, ubicación o requisitos.

*Solución:*
Se desarrolló un módulo de *limpieza y estandarización de texto*, eliminando ruido, normalizando espacios y extrayendo metadatos relevantes.

---

### Clasificación las ofertas

Se implementó un sistema dual:

#### a) *Reglas basadas en palabras clave (regex)*

Ejemplos:

* “call center”, “asesor”, “BPO” → *Call center/BPO*
* “bodega”, “logística”, “planta” → *Logística/Bodega*
* “cajero”, “ventas”, “tienda” → *Retail/Comercial*

#### b) *Modelo de inteligencia artificial (OpenAI GPT-5o)*

El modelo recibe:

* Texto completo de la oferta
* Cargo, experiencia, salario, ubicación
* Sugerencia de categoría por reglas

Y devuelve:

* *Categoría principal*
* *Subcategoría específica*
* *Nivel de confianza*

Se valida la salida para garantizar que pertenezca a una de las categorías definidas.

### ¿Qué información se obtiene de cada oferta?

* Categoría y subcategoría laboral
* Información clave (cargo, experiencia, salario, ubicación, requisitos)
* Clasificación preliminar CNO/CUOC
* Nivel de confianza de la IA
* Texto limpio y normalizado

Esto permite construir indicadores como:

* Sectores con mayor oferta
* Regiones con más demanda laboral
* Rango salarial por categoría
* Frecuencia de contratos formales e informales

---

## Stack Tecnológico

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-orange)
![OpenAI API](https://img.shields.io/badge/OpenAI-API-green)
![Regex](https://img.shields.io/badge/Regex-text_processing-lightgrey)

*Componentes principales del proyecto:*

* *Python 3.11*
* Librerías: selenium, pandas, re, json, openai
* *Jupyter Notebooks* para prototipos
* Automatización del scraping y clasificación
* Archivos de salida en formato JSON

---

## Cómo Empezar

1. Clonar el repositorio
2. Configurar entorno (Poetry o venv)
3. Ingresar la *OPENAI_API_KEY* en un archivo .env
4. Ejecutar el pipeline con:

bash
python src/clasificacion_ofertas.py




## Estructura del Repositorio

* */data*: Datos crudos y clasificados
* */notebooks*: Exploración y pruebas
* */src*: Scripts de scraping, limpieza y clasificación
* */docs*: Informe, documentación y diagramas
* *README.md*: Manual principal del proyecto



## Datos y Fuentes

*Fuente principal:*

* Canal de WhatsApp que publica ofertas laborales en Colombia.
  Las ofertas se extraen automáticamente mediante Selenium y WhatsApp Web.

*Tipos de información extraída:*

* Texto del anuncio
* Cargo declarado
* Ubicación
* Salario (si está disponible)
* Experiencia y requisitos

*Salida final:*
analisis_ofertas_empleo_clasificado.json

---

## Metodología

### Fase 1 — Recolección (web scraping)

* Acceso automático a WhatsApp Web
* Extracción de todos los mensajes del canal
* Eliminación de duplicados


### Fase 2 — Limpieza y organización

* Normalización de texto
* Eliminación de símbolos y emojis
* Detección de campos relevantes (regex)
* Conversión a estructura JSON

### Fase 3 — Clasificación (reglas + IA)

* Aplicación de reglas por palabras clave
* Clasificación con modelo OpenAI
* Fusión de ambas clasificaciones
* Validación y selección de categoría final

### Fase 4 — Integración ocupacional (CNO/CUOC)

* Mapeo preliminar de categorías a ocupaciones
* Preparación para futura clasificación automática con IA

