# Generador de portafolios de evidencias

[**Descargar el script generar_portafolio.py**](./generar_portafolio.py)

El script lee los títulos de una plantilla de Word, propone una carpeta para cada sección y coloca marcadores en una copia. Durante el parcial puedes ir guardando evidencias y generar borradores editables para revisar el orden, la legibilidad y los apartados pendientes.

Si el enlace abre el código en GitHub, pulsa **Download raw file** para guardar el `.py`. Para copiar los comandos, abre esta guía en la vista renderizada de GitHub y usa el icono **Copiar** que aparece en la esquina superior derecha de cada bloque de PowerShell. [Botón de copia en los bloques de código de GitHub](https://github.blog/news-insights/product-news/whats-new-from-github-changelog-may-2021-recap/)

## Requisitos

- Windows con PowerShell y Python 3.11, la versión con la que se verificó la guía.
- Word para preparar la plantilla `.docx` y revisar los borradores.
- Una plantilla del profesor y las evidencias en `.pdf`, `.jpg`, `.jpeg` o `.png`. Para incorporar una hoja de Excel como evidencia visible, expórtala a PDF antes de guardarla en el proyecto.

Si necesitas instalar Python, descárgalo desde su sitio oficial y abre una terminal nueva después de la instalación. [Python para Windows](https://www.python.org/downloads/windows/)

## 1. Instala las bibliotecas

Guarda el script y el Word del profesor en la misma carpeta. En esta guía el Word se llama `plantilla.docx`. Abre esa carpeta en el Explorador de archivos, escribe `powershell` en la barra de direcciones y presiona Enter.

Comprueba que Python esté disponible.

```powershell
python --version
```

Crea un entorno para el proyecto e instala las dependencias. Si tu instalación usa el comando `py`, cambia la primera línea por `py -3.11 -m venv .venv`.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pymupdf==1.28.2 python-docx==1.2.0
```

Comprueba que el generador arranque. Debes ver las opciones `--preparar` y `--proyecto`.

```powershell
.\.venv\Scripts\python.exe generar_portafolio.py --help
```

## 2. Prepara el proyecto al inicio del parcial

En Word, aplica **Título 1** a los apartados principales y **Título 2** a sus subsecciones. Para un semestre completo, puedes usar **Título 1** para cada parcial y **Título 2** para sus evidencias. Comprueba la jerarquía en **Vista → Panel de navegación → Títulos**. Guarda la plantilla.

```powershell
.\.venv\Scripts\python.exe generar_portafolio.py --preparar plantilla.docx --proyecto Parcial_1
```

El script muestra una lista numerada. Escribe, por ejemplo, `2,3` si esos números corresponden a las secciones que recibirán archivos en tu plantilla. Puedes reservar *Objetivo*, *Conclusión* o *Reflexión* para redactarlos en Word.

El proyecto se guarda en `Parcial_1`. Dentro encontrarás una **copia de la plantilla** con marcadores, el archivo `secciones.json` que relaciona cada marcador con su carpeta, y `evidencias`, con las subcarpetas de los apartados elegidos. La plantilla original queda disponible para reutilizarla.

## 3. Guarda las evidencias durante el parcial

Dentro de `Parcial_1\evidencias`, abre la subcarpeta que corresponda a cada actividad y guarda ahí los archivos. Consulta `secciones.json` si necesitas confirmar una ruta. Usa prefijos como `01_actividad.pdf` y `02_rubrica.pdf` para controlar el orden dentro de la sección. Si escaneaste un cuaderno como PDF, el script insertará cada página como imagen. Las fotos JPG y PNG se insertan directamente.

## 4. Genera y revisa el borrador en Word

```powershell
.\.venv\Scripts\python.exe generar_portafolio.py --proyecto Parcial_1
```

Abre `Parcial_1\portafolio_generado.docx`. El script coloca cada página del PDF o imagen en una hoja nueva y escribe **Evidencia pendiente** en las secciones vacías. Revisa que las páginas sean legibles, agrega tus comentarios o reflexiones y, si la plantilla tiene una tabla de contenido de Word, selecciona **Actualizar toda la tabla** después de editar.

Al repetir el comando, se crean versiones como `portafolio_generado_02.docx`. Cada versión parte de `Parcial_1\plantilla.docx`. Si quieres que un texto aparezca en los borradores futuros, agrégalo a esa copia de la plantilla y conserva los marcadores.

## Prueba rápida

Prepara un proyecto con dos secciones. Guarda un PDF de dos páginas en la primera carpeta y deja la segunda vacía. El primer borrador debe mostrar ambas páginas y un aviso de evidencia pendiente. Agrega una imagen a la segunda carpeta y vuelve a generar. La versión `_02` debe mostrar la imagen en su sección, y el primer borrador debe seguir disponible.

## Si algo falla

| Situación | Qué revisar |
|---|---|
| PowerShell no encuentra el script | Abre PowerShell en la carpeta donde guardaste `generar_portafolio.py`. Si descargaste un archivo de texto, verifica que el nombre termine en `.py`. |
| Aparece `ModuleNotFoundError` | Instala las dependencias con el Python de `.venv` y ejecuta los comandos con ese mismo Python. |
| Un título no aparece al preparar | Aplica un estilo de título al párrafo en el cuerpo del Word. La detección se basa en los niveles de título. |
| El proyecto ya existe | Usa solo `--proyecto Parcial_1` para generar otro borrador, o elige un nombre diferente para preparar otro proyecto. |
| Una sección sigue pendiente | Verifica la ruta en `secciones.json` y guarda el archivo compatible directamente en esa carpeta. |
| Una imagen se ve muy pequeña | Revisa la orientación del original y los márgenes de la plantilla. El script ajusta las imágenes al espacio de la primera sección de Word. |
