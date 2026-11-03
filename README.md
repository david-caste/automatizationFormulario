# Registro de Guías y Clientes

## Usar en macOS

La aplicación también funciona en macOS. Para ejecutarla desde el código:

1. Instala Python 3 desde [python.org](https://www.python.org/downloads/macos/).
   Asegúrate de que esa instalación incluya Tcl/Tk; puedes comprobarlo con
   `python3 -m tkinter`.
2. Desde esta carpeta, instala las dependencias y ejecuta la aplicación:

   ```sh
   python3 -m pip install -r requirements.txt
   python3 app.py
   ```

## Descargar una aplicación `.app`

El workflow de GitHub Actions construye versiones para Apple Silicon y Mac
Intel. Después de una ejecución correcta, descarga el ZIP correspondiente
desde **Actions → Build macOS app → Artifacts** y descomprímelo en el Mac.

El workflow se ejecuta al subir cambios a `main` o manualmente desde la pestaña
**Actions**. Para abrir la aplicación, haz doble clic en
`Registro de Guias.app`. Como no está firmada ni notarizada, macOS podría
bloquearla; si confías en el archivo, haz clic derecho en la aplicación,
selecciona **Abrir** y confirma.

Cada archivo ZIP contiene una aplicación para una sola arquitectura: Apple
Silicon (`arm64`) o Intel (`x86_64`). El empaquetado de Windows existente no
cambia.
