# WhatsApp Empleo Bot

Este proyecto automatiza la extracción de ofertas de empleo desde un canal o chat de WhatsApp en **WhatsApp Web**, y las guarda en formato CSV y Excel para analizarlas.

##  Características
- Guarda mensajes sin duplicados en `data/ofertas.csv` y `data/ofertas.xlsx`.
- Configurable a través de un archivo `.env`.
- Incluye un script de análisis (`analisis.py`).

##  Instalación
```bash
conda create -n whatsappbot python=3.11 -y
conda activate whatsappbot
pip install -r requirements.txt
