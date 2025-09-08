
# Bot de empleo de WhatsApp (canal)

Automatiza la captura de ofertas publicadas en **un canal de WhatsApp** y las guarda en **SQLite** y en **CSV**.
Cuando detecta nuevas ofertas, hace **commit & push** al repositorio automáticamente.

> ⚠️ Usa esto solo con permiso y sin exponer datos sensibles (p. ej., correos/teléfonos) si el repositorio es público.

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

## Paso a paso (GitHub Web)

1) Descarga este proyecto como **ZIP** desde el enlace que te pasé en el chat.
2) Descomprime el ZIP en tu computador.
3) En tu repositorio de GitHub (p. ej. *Bot de empleo de WhatsApp*), ve a **Código → Agregar archivo → Subir archivos**.
4) Arrastra la **carpeta y archivos** descomprimidos (puedes arrastrar carpetas completas).
5) Escribe un mensaje de confirmación y pulsa **Commit** a la rama principal.

> Si GitHub no te deja arrastrar carpetas, sube primero los archivos de la raíz (README.md, requirements.txt, .gitignore, .env.example) y luego, en la misma pantalla, arrastra la carpeta `src` y las carpetas `data` y `db`. Los `.gitkeep` permiten subir carpetas vacías.

## Configuración local y ejecución

> Necesitas **Python 3.10+** y **Git** instalados.

```bash
# Clona tu repo y entra a la carpeta
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
CHANNEL_URL=https://whatsapp.com/channel/XXXXXXXXXX   # tu enlace de canal
REPO_PATH=                                            # deja vacío para autodetectar
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

## Problemas comunes
- **No empuja a GitHub**: asegúrate de tener permisos para `origin` (token HTTPS o SSH) y que `git remote -v` apunta a tu repo.
- **No detecta textos**: la UI de WhatsApp Web cambia. Edita los selectores en `SELECTORS_CANDIDATOS` y `MSG_TEXT_SELECTORS` en `watcher.py`.
- **Se cierra la sesión**: vuelve a correr `python src/watcher.py` y escanea el QR otra vez.
