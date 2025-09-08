
# Bot de empleo de WhatsApp (canal)

Automatiza la captura de ofertas publicadas en **un canal de WhatsApp** y las guarda en **SQLite** y en **CSV**.
Cuando detecta nuevas ofertas, hace **commit & push** al repositorio automáticamente.

## Estructura

```
.
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ .env.example
├─ data/
│  └─ .gitkeep
├─ db/
│  └─ .gitkeep
└─ src/
   ├─ watcher.py
   ├─ parser.py
   ├─ db.py
   ├─ push.py
   └─ utils.py
```

## Configuración local y ejecución

> Necesitas **Python 3.10+** y **Git** instalados.

```bash

git clone <URL_DE_TU_REPO>
cd <carpeta_del_repo>

# Crea entorno e instala dependencias
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
python -m playwright install
```

Copia `.env.example` a `.env` y edita los valores:

```
CHANNEL_URL=https://whatsapp.com/channel/XXXXXXXXXX  
REPO_PATH=                                            
REMOTE_NAME=origin
BRANCH=main   # o 'principal' si tu rama se llama así
```

Opcional: configura Git si no lo has hecho ya (solo una vez por máquina):

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@correo.com"
```

### Ejecuta el bot

```bash
# Desde la carpeta raíz del repo (donde está README.md)
python src/watcher.py
```

- La primera vez se abrirá **WhatsApp Web** y te pedirá escanear el **QR**.
- El bot leerá los últimos mensajes del **canal** y cada 5 segundos revisará si hay nuevos.
- Cuando detecte una **oferta**, la guardará en `db/ofertas.sqlite`, exportará `data/ofertas.csv` y hará **commit & push** si hay cambios.

### Verifica resultados
- Revisa `data/ofertas.csv` (debería crecer cuando haya nuevas ofertas).
- En GitHub, mira los commits automáticos con el mensaje `chore(data): oferta ...`.

## Personalización
- Ajusta las **regex** en `src/parser.py` si el canal tiene una plantilla fija (Empresa, Cargo, Ubicación, etc.).
- En `watcher.py`, la función `parece_oferta()` filtra mensajes que parezcan vacantes para evitar ruido.

