# Visual-Bolt

Esta pequeña aplicación genera un boceto de perno de anclaje utilizando **Python** y **Matplotlib**. El servidor **FastAPI** recibe las medidas y devuelve una imagen PNG con las cotas (medidas) distribuídas alrededor del perno. El dibujo es en 2D con un estilo similar a un plano técnico.

## Estructura del proyecto

```
main.py             # Servidor FastAPI y generación de la imagen con matplotlib
static/index.html   # Formulario HTML para solicitar las medidas
```

Mantener los archivos separados facilita modificar la lógica de servidor o la interfaz por separado. El archivo `main.py` contiene todo el código de generación y es conveniente dejar la plantilla HTML en la carpeta `static` para poder cambiarla sin tocar el servidor.

El formulario solicita las medidas en el siguiente orden para facilitar la lectura:

1. **D** - diámetro del perno
2. **L** - largo total
3. **C** - largo del gancho
4. **T** - longitud de la rosca

Los mismos nombres se utilizan como parámetros en la URL.

## Ejecución

Con Python 3 instalado solo debes ejecutar:

```bash
uvicorn main:app --reload
```

Abre `http://localhost:8000` en tu navegador. Llena el formulario y presiona **Generar** para obtener el boceto. El resultado se muestra en una nueva página con un enlace para descargar la imagen PNG.
