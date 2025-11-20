<h1>Informe Técnico: Análisis automatizado de ofertas laborales publicadas en un canal de WhatsApp</h1>


# **1. Introducción**

El presente informe documenta el desarrollo, implementación y ejecución de un pipeline automatizado para la extracción, limpieza, estructuración y análisis estadístico de mensajes asociados a ofertas laborales publicados en un canal de WhatsApp denominado *“Empleo en Bogotá”*.
El sistema se diseñó para transformar mensajes desestructurados en un dataset analítico, facilitando la generación de estadísticas laborales y métricas clave relevantes para el mercado de empleo local.

Los datos analizados provienen de un archivo CSV con 469 mensajes capturados mediante web scraping.

---

# **2. Objetivo del trabajo**

El objetivo principal fue construir un proceso integral capaz de:

1. **Limpieza profunda del texto**: eliminación de ruido, emojis, URLs y caracteres irrelevantes.
2. **Depuración de duplicados**.
3. **Extracción automatizada de información estructurada**: cargo, empresa, ubicación, salario, nivel educativo, contrato, experiencia, vacantes y datos de eventos.
4. **Análisis estadístico descriptivo y salarial**.
5. **Construcción de un dataset final apto para análisis avanzado**: machine learning futuro.
6. **Exportación** en formatos JSON y Excel conforme a estándares de interoperabilidad.
7. **Generación de reporte consolidado de hallazgos**.

---

# **3. Herramientas, librerías y tecnologías utilizadas**

Durante el pipeline se emplearon las siguientes herramientas:

### **3.1. Librerías de Python**

* **pandas**: manipulación y transformación de datos.
* **numpy**: operaciones numéricas.
* **re (regex)**: extracción de patrones textuales.
* **json**: serialización y exportación de resultados.
* **datetime**: manejo temporal.
* **fuzzywuzzy / difflib**: similitud y detección de coincidencias textuales.
* **unicodedata**: normalización de caracteres.
* **warnings**: manejo de advertencias.
* **openpyxl**: exportación de archivos Excel.

### **3.2. Lenguaje y entorno**

* Python 3.x
* Pipeline ejecutado en entorno local.

---

# **4. Flujo de trabajo aplicado (Pipeline)**

El trabajo implementado sigue una arquitectura modular de nueve etapas, integradas en la función `pipeline_completo()`.

---

## **4.1. Carga y exploración inicial de datos**

* Se importó el archivo **mensajes.csv**.
* Se obtuvieron 469 mensajes originales.
* Columnas detectadas:

  * `id`
  * `remitente`
  * `contenido`
  * `fecha_hora`

Se verificó consistencia de formatos y presencia de los campos requeridos.

---

## **4.2. Limpieza de texto**

Se aplicó la función `limpiar_texto()` con los siguientes procesos:

* Eliminación de URLs (regex).
* Eliminación de emojis y caracteres especiales.
* Normalización Unicode.
* Eliminación de dobles espacios y caracteres no deseados.
* Conversión a formato estándar.

---

## **4.3. Eliminación de duplicados**

Se creó una columna temporal con texto limpio para estandarizar comparaciones.

Resultados obtenidos:

* **469 mensajes originales**
* **61 mensajes únicos** después de eliminar duplicados exactos.
* **46 mensajes relevantes** (filtrados por longitud > 50 caracteres), usualmente ofertas completas.

---

## **4.4. Extracción de información de ofertas**

Se desarrolló un extractor basado en expresiones regulares y heurísticas lingüísticas para identificar:

* Cargo
* Empresa
* Ciudad / ubicación
* Nivel educativo requerido
* Tipo de contrato
* Experiencia mínima
* Número de vacantes
* Salario
* Fechas y lugares de eventos de contratación

Ejemplos observados en el dataset:

* Cargo extraído: *"bachilleres Convocatoria de empleo presencial..."*
* Ubicación frecuente: *Bogotá*, *Chapinero*, *Bosa*.
* Nivel educativo detectado: *Bachiller*, *Técnico*, etc.
* Empresas extraídas cuando contenían sufijos como SAS, LTDA, S.A.S.

---

## **4.5. Consolidación del dataset**

Los datos limpios y los campos extraídos se integraron en un dataframe denominado **df_procesado**, posteriormente usado para análisis.

---

## **4.6. Análisis estadístico descriptivo**

Se generaron las siguientes métricas:

### **Resumen general:**

* Total de ofertas procesadas: 46
* Ofertas con cargo identificado: alta proporción
* Empresas únicas detectadas: extracción parcial (muchas ofertas sin empresa explícita)

### **Ocupaciones más demandadas:**

Se observaron patrones repetitivos asociados a:

* Bachilleres
* Operarios logísticos
* Cargos varios en sector servicios

### **Ubicaciones más frecuentes:**

* Bogotá
* Chapinero
* Bosa

### **Niveles educativos:**

* Mayor volumen: **Bachiller**
* Menor volumen: Técnico, tecnólogo, profesional
  (esto indica una fuerte demanda de mano de obra operativa).

---

## **4.7. Análisis de salarios**

Métodos aplicados:

* Extracción numérica con regex.
* Normalización (miles, millones, ruidos).
* Categorización según SMMLV 2025 (1.423.500 COP).

Resultados clave:

* Identificación de salarios válidos en una parte de las ofertas.
* Rango salarial observado:

  * mínimo válido > 1.000.000 COP
  * Salarios categorizados en rangos:

    * 1–2 SMMLV
    * 2–3 SMMLV
    * 3–5 SMMLV
* Cálculo de:

  * salario promedio
  * salario mediana
  * salarios por ocupación (cuando había más de una oferta comparable).

---

## **4.8. Exportación de resultados**

El pipeline generó dos archivos finales:

### **1. analisis_ofertas_empleo.json**

Incluye:

* Metadatos del análisis
* Estadísticas descriptivas completas
* Dataset de ofertas estructurado

### **2. ofertas_procesadas.xlsx**

Dataset final íntegro, usable para análisis posteriores.

La función `preparar_para_json()` garantizó compatibilidad con estándares JSON:

* Conversión de objetos Pandas, NumPy y fechas.
* Limpieza de nulos.
* Normalización de estructuras.

---

## **4.9. Generación de reporte estadístico final**

Se imprimió en consola un resumen organizado incluyendo:

* Resumen general
* Top ocupaciones
* Distribución geográfica
* Requisitos educativos
* Salarios
* Rangos salariales

Este reporte sirve como insumo para toma de decisiones y análisis laboral.

---

# **5. Análisis general de los resultados**

Del análisis realizado pueden destacarse las siguientes conclusiones:

### **1. Predominio de ofertas para perfiles operativos**

La mayoría de ofertas están dirigidas a bachilleres y cargos logísticos o de servicios.

### **2. Alta redundancia en la información**

De 469 mensajes, solo 61 eran únicos, lo que evidencia alta repetición en el canal.

### **3. Información empresarial incompleta**

Muchas ofertas no mencionan claramente el nombre de la empresa contratante.

### **4. Niveles de educación exigidos**

Hay poca presencia de niveles técnicos, tecnólogos o profesionales.

### **5. Variabilidad salarial**

Se observó dispersión salarial moderada, concentrada en un rango de 1–3 SMMLV.

### **6. Importancia de Bogotá como núcleo**

La mayoría de las ofertas están geográficamente focalizadas en la ciudad de Bogotá.

---

# **6. Conclusiones**

El pipeline desarrollado constituye una herramienta robusta para procesar texto no estructurado proveniente de canales informales de empleo, demostrando un proceso eficaz de limpieza y depuración, una extracción consistente de información clave mediante reglas textuales, la generación de estadísticas laborales útiles para la caracterización sectorial y la producción de archivos finales aptos para visualización, elaboración de dashboards y construcción de modelos predictivos.

