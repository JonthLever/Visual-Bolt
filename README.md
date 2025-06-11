# Visual-Bolt

Esta pequeña aplicación permite generar un boceto sencillo de un perno de anclaje según medidas ingresadas por el usuario. Se apoya en **FastAPI** para servir la página y en **HTML5 canvas** para dibujar el perno con JavaScript.

## Estructura del proyecto

```
main.py             # Servidor FastAPI que entrega la página
static/index.html   # Página con el formulario y el código de dibujo
```

Mantener los archivos separados facilita modificar la lógica de servidor o de interfaz por separado, pero el proyecto es lo suficientemente pequeño para mantenerse simple.

## Ejecución

Con Python 3 instalado solo debes ejecutar:

```bash
uvicorn main:app --reload
```

Luego abre `http://localhost:8000` en el navegador. Introduce las medidas, selecciona el tipo de perno (recto, L o J) y presiona **Dibujar** para ver el boceto.

