# Visual-Bolt

Esta pequeña aplicación genera un boceto de perno de anclaje utilizando **Python**. Se usa **FastAPI** para recibir las medidas y devolver un archivo SVG con cotas (medidas) que puede mostrarse o descargarse desde el navegador. El dibujo es en 2D e incluye el grosor del perno.

## Estructura del proyecto

```
main.py             # Servidor FastAPI y generación del SVG
static/index.html   # Formulario HTML para solicitar las medidas
```

Mantener los archivos separados facilita modificar la lógica de servidor o la interfaz por separado. El archivo `main.py` contiene todo el código de generación y es conveniente dejar la plantilla HTML en la carpeta `static` para poder cambiarla sin tocar el servidor.

## Ejecución

Con Python 3 instalado solo debes ejecutar:

```bash
uvicorn main:app --reload
```

Abre `http://localhost:8000` en tu navegador. Llena el formulario y presiona **Generar** para obtener el boceto. El resultado se muestra en una nueva página con un enlace para descargar el SVG.