# Visual-Bolt
Graphical representation of custom anchor bolts, by simply entering certain measurements

Esta pequeña aplicación genera un boceto de perno de anclaje utilizando **Python** y **Matplotlib**. El servidor **FastAPI** recibe las medidas y devuelve una imagen PNG con las cotas (medidas) distribuídas alrededor del perno. El dibujo es en 2D con un estilo similar a un plano técnico.

La aplicación funciona únicamente con las bibliotecas disponibles en el entorno (FastAPI y Matplotlib). Para mantener las dependencias al mínimo, los cálculos de la curva tipo J se realizan con funciones básicas de `math` y no requieren NumPy.

El boceto se crea con la función `draw_bolt_diagram`, la cual acepta el tipo de perno (`L` o `J`) y las dimensiones **D**, **L**, **C** y **T**. Para el tipo **J** se puede ajustar el parámetro adicional `closing_angle` (grados) que determina cuánto se cierra la curva del gancho. La sección roscada se indica con un rectángulo rayado (`////`) sobre el cuerpo negro del perno y se utilizan líneas de referencia rojas para marcar las medidas.

## Estructura del proyecto

```
main.py             # Servidor FastAPI y generación de la imagen con matplotlib
static/index.html   # Formulario HTML para solicitar las medidas
```

Mantener los archivos separados facilita modificar la lógica de servidor o la interfaz por separado. El archivo `main.py` contiene todo el código de generación y es conveniente dejar la plantilla HTML en la carpeta `static` para poder cambiarla sin tocar el servidor.

La página principal (`/`) permite introducir las medidas y elegir el tipo de perno. Al enviar el formulario se redirige a `/draw`, donde se muestra la imagen generada y un enlace para descargarla como PNG.

El formulario solicita las medidas en el siguiente orden para facilitar la lectura:

1. **D** - diámetro del perno
2. **L** - largo total
3. **C** - largo del gancho
4. **T** - longitud de la rosca
5. **closing_angle** - ángulo de cierre del gancho (solo tipo J)

Para un perno tipo **L** se dibuja un gancho recto a 90°. El perno tipo **J** forma una curva con radio 4×D; el parámetro `closing_angle` permite controlar cuánto gira la curva (180° por defecto). Si **C** es mayor a la longitud de la curva se agrega un tramo recto al final.

Los mismos nombres se utilizan como parámetros en la URL.
Para el parámetro `closing_angle` basta con incluirlo solo si se quiere un ángulo diferente a 180°.

## Ejecución

Con Python 3 instalado solo debes ejecutar:

```bash
uvicorn main:app --reload
```

Abre `http://localhost:8000` en tu navegador. Llena el formulario y presiona **Generar** para obtener el boceto. El resultado se muestra en una nueva página con un enlace para descargar la imagen PNG.

## Interfaz interactiva con Gradio

Para obtener un diagrama que se actualice en tiempo real puedes ejecutar `gradio_app.py`:

```bash
python3 gradio_app.py
```

Se abrirá una interfaz web donde podrás elegir el tipo de perno (**L** o **J**) y los valores de **D**, **L**, **C**, **T** y **closing_angle**. Al modificar cualquier parámetro la imagen se actualiza mostrando:

- Las cotas de diámetro, gancho, rosca y longitud total
- Un texto con la longitud del arco calculada mediante `4×D × radians(closing_angle)`
- Un texto con la longitud total del perno (largo recto + arco)

La imagen puede descargarse desde el botón de Gradio.