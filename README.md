# Visual-Bolt
El boceto se crea con la función `draw_bolt_diagram`, la cual acepta el tipo de perno (`L` o `J`) y las dimensiones **D**, **L**, **C** y **T**. El área roscada se muestra con un rayado gris y se utilizan líneas de referencia rojas para marcar las medidas.

La página principal (`/`) permite introducir las medidas y elegir el tipo de perno. Al enviar el formulario se redirige a `/draw`, donde se muestra la imagen generada y un enlace para descargarla como PNG.

Para un perno tipo **L** se dibuja un gancho recto a 90°. El perno tipo **J** forma una curva con radio 4×D y, en caso de que **C** sea mayor, se agrega un tramo recto al final de la curva.

Graphical representation of custom anchor bolts, by simply entering certain measurements

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