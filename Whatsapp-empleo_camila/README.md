
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

git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO

python -m venv .venv
.\.venv\Scripts\activate

pip install -r requirements.txt
python -m playwright install

copy .env.example .env

```

CHANNEL_URL=https://whatsapp.com/channel/0029VaiShJNBvvsiioOo7c0U
REPO_PATH=
REMOTE_NAME=origin
BRANCH=main


```


```

Opcional: configura Git si no lo has hecho ya (solo una vez por máquina):

```bash
git config --global user.name "Camila Reyes"
git config --global user.email "camiandreareyes2@gmail.com"
```

### Ejecutar el bot

```bash
# Desde la carpeta raíz del repo (donde está README.md)
python src/watcher.py
```


