import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

import pymupdf
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from docx.text.paragraph import Paragraph


SECCIONES_DE_PRUEBA = {"[[APUNTES]]": "apuntes", "[[WORKBOOK]]": "workbook"}
EXTENSIONES = {".pdf", ".jpg", ".jpeg", ".png"}


@dataclass
class Seccion:
    nivel: int
    titulo: str
    carpeta: Path
    ancla: Paragraph
    marcador: Paragraph | None = None


def nivel_de_titulo(parrafo):
    propiedades = parrafo._p.pPr
    if propiedades is not None and propiedades.outlineLvl is not None:
        return int(propiedades.outlineLvl.val) + 1

    estilo = parrafo.style
    while estilo is not None:
        coincidencia = re.fullmatch(r"Heading([1-9])", estilo.style_id)
        if coincidencia:
            return int(coincidencia[1])
        estilo = estilo.base_style
    return 10


def detectar_secciones(documento):
    secciones = []
    padres = []
    for parrafo in documento.paragraphs:
        titulo = parrafo.text.strip()
        if not titulo:
            continue
        nivel = nivel_de_titulo(parrafo)
        if nivel <= 9:
            while padres and padres[-1].nivel >= nivel:
                padres.pop()
            nombre = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
            nombre = re.sub(r"[^a-z0-9]+", "_", nombre.lower()).strip("_")[:40]
            base = padres[-1].carpeta if padres else Path("evidencias")
            carpeta = base / f"{len(secciones) + 1:02d}_{nombre or 'seccion'}"
            seccion = Seccion(nivel, titulo, carpeta, parrafo)
            secciones.append(seccion)
            padres.append(seccion)
        elif secciones:
            seccion = secciones[-1]
            if titulo in SECCIONES_DE_PRUEBA or re.fullmatch(r"\[\[EVIDENCIA_\d+\]\]", titulo):
                if seccion.marcador is not None:
                    raise ValueError(f"Hay más de un marcador bajo «{seccion.titulo}».")
                seccion.marcador = parrafo
            else:
                seccion.ancla = parrafo
    return secciones


def quitar_parrafo(parrafo):
    parrafo._p.getparent().remove(parrafo._p)


def preparar_proyecto(plantilla, destino):
    if destino.exists():
        raise ValueError(f"Ya existe {destino}. Elige otra carpeta con --proyecto.")
    documento = Document(plantilla)
    secciones = detectar_secciones(documento)
    if not secciones:
        raise ValueError("Aplica los estilos Título 1, Título 2, etc., en Word e inténtalo de nuevo.")

    print("Secciones encontradas")
    for numero, seccion in enumerate(secciones, 1):
        sangria = "  " * (seccion.nivel - 1)
        print(f"{numero:2}. {sangria}{seccion.titulo}  →  {seccion.carpeta.as_posix()}")
    respuesta = input("\nEscribe los números de las secciones que recibirán archivos (ej. 3,4,8): ")
    if not respuesta.strip():
        print("Preparación cancelada.")
        return
    seleccion = {int(numero.strip()) for numero in respuesta.split(",")}
    if not seleccion.issubset(range(1, len(secciones) + 1)):
        raise ValueError("Elige solo números de la lista.")

    rutas = {}
    textos = {parrafo.text.strip() for parrafo in documento.paragraphs}
    siguiente = 1
    for numero, seccion in enumerate(secciones, 1):
        if numero not in seleccion:
            if seccion.marcador is not None:
                quitar_parrafo(seccion.marcador)
            continue

        if seccion.marcador is not None:
            marcador = seccion.marcador.text.strip()
        else:
            marcador = f"[[EVIDENCIA_{siguiente:02d}]]"
            while marcador in textos:
                siguiente += 1
                marcador = f"[[EVIDENCIA_{siguiente:02d}]]"
            textos.add(marcador)
            parrafo = documento.add_paragraph(marcador)
            seccion.ancla._p.addnext(parrafo._p)
        if marcador in rutas:
            raise ValueError(f"El marcador {marcador} está repetido.")
        rutas[marcador] = seccion.carpeta.as_posix()

    with TemporaryDirectory(dir=destino.parent) as temporal:
        proyecto = Path(temporal) / "proyecto"
        for ruta in rutas.values():
            (proyecto / ruta).mkdir(parents=True, exist_ok=True)
        documento.save(proyecto / "plantilla.docx")
        (proyecto / "secciones.json").write_text(
            json.dumps(rutas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        proyecto.rename(destino)
    print(f"Proyecto preparado en {destino}")


def imagenes_de(archivo):
    if archivo.suffix.lower() == ".pdf":
        with pymupdf.open(archivo) as pdf:
            for pagina in pdf:
                imagen = pagina.get_pixmap(dpi=200, alpha=False)
                yield BytesIO(imagen.tobytes("png"))
    else:
        yield str(archivo)


def generar_portafolio(carpeta, proyecto_preparado):
    documento = Document(carpeta / "plantilla.docx")
    seccion = documento.sections[0]
    ancho = seccion.page_width - seccion.left_margin - seccion.right_margin
    alto = seccion.page_height - seccion.top_margin - seccion.bottom_margin
    alto -= Inches(0.35)  # Espacio para el párrafo que contiene la imagen

    secciones = SECCIONES_DE_PRUEBA
    if proyecto_preparado:
        secciones = json.loads((carpeta / "secciones.json").read_text(encoding="utf-8"))

    for marcador, subcarpeta in secciones.items():
        coincidencias = [p for p in documento.paragraphs if p.text.strip() == marcador]
        if len(coincidencias) != 1:
            raise ValueError(f"La plantilla debe contener un solo párrafo {marcador}")

        origen = carpeta / subcarpeta
        archivos = sorted(
            archivo for archivo in origen.iterdir()
            if archivo.is_file() and archivo.suffix.lower() in EXTENSIONES
        ) if origen.is_dir() else []
        ancla = coincidencias[0]
        if not archivos:
            if not proyecto_preparado:
                raise ValueError(f"No hay evidencias compatibles en {subcarpeta}")
            ancla.text = f"Evidencia pendiente. Carpeta: {subcarpeta}"
            continue

        for archivo in archivos:
            for imagen in imagenes_de(archivo):
                parrafo = ancla.insert_paragraph_before(style="Normal")
                parrafo.paragraph_format.page_break_before = True
                parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER

                foto = parrafo.add_run().add_picture(imagen)
                escala = min(ancho / foto.width, alto / foto.height, 1)
                foto.width = round(foto.width * escala)
                foto.height = round(foto.height * escala)

        quitar_parrafo(ancla)

    salida = carpeta / "portafolio_generado.docx"
    if proyecto_preparado:
        version = 1
        with TemporaryDirectory(dir=carpeta) as temporal:
            borrador = Path(temporal) / salida.name
            documento.save(borrador)
            while True:
                try:
                    borrador.rename(salida)
                    break
                except FileExistsError:
                    version += 1
                    salida = carpeta / f"portafolio_generado_{version:02d}.docx"
    else:
        documento.save(salida)
    print(f"Borrador guardado en {salida}")


def main():
    parser = argparse.ArgumentParser(description="Prepara y arma un portafolio de evidencias.")
    parser.add_argument("--preparar", type=Path, metavar="PLANTILLA", help="Word original del profesor")
    parser.add_argument("--proyecto", type=Path, help="Carpeta del proyecto")
    args = parser.parse_args()
    try:
        if args.preparar:
            destino = (args.proyecto or Path("Proyecto_portafolio")).resolve()
            preparar_proyecto(args.preparar, destino)
        else:
            carpeta = args.proyecto or Path(__file__).resolve().parent
            generar_portafolio(carpeta, args.proyecto is not None)
    except (ValueError, OSError, EOFError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
