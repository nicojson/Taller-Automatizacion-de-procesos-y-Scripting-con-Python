import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "9142709630:AAGNbFL7zRX1tJwoPFws5f2HTUkbSsafxG4"  # Pega aquí el token de BotFather
CHAT_ID = "8658331156"           # Pega aquí tu ID de userinfobot
URL = "https://sii.celaya.tecnm.mx/residencias-publicas/y9sXXxE9JMKXRonyeRBiDRyPKbIKIL4pPUXqjGOTYGL6JQ"

# 1. Función para raspar y filtrar el portal del TecNM Celaya
def buscar_vacantes_por_carrera(carrera_filtro):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(URL, headers=headers)

    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    articulos = soup.find_all("article")

    resultados = []
    carrera_filtro = carrera_filtro.lower()

    for art in articulos:
        texto_completo = art.get_text(separator=" ", strip=True).lower()

        # Filtro: coincide con la carrera seleccionada o es general
        if carrera_filtro == "todas" or carrera_filtro in texto_completo or "todas las carreras" in texto_completo:
            empresa = art.find("h5").get_text(strip=True) if art.find("h5") else "Empresa N/A"
            parrafos = art.find_all("p")
            descripcion = parrafos[0].get_text(strip=True) if parrafos else "Sin detalle"

            resultados.append({
                "empresa": empresa,
                "descripcion": descripcion
            })

    return resultados

# 2. Comando /start: Muestra los botones de carrera
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("💻 Sistemas", callback_data="sistemas"),
            InlineKeyboardButton("⚙️ Mecatrónica", callback_data="mecatrónica"),
        ],
        [
            InlineKeyboardButton("🌱 Ambiental", callback_data="ambiental"),
            InlineKeyboardButton("🏭 Industrial", callback_data="industrial"),
        ],
        [
            InlineKeyboardButton("🌐 Mostrar Todas", callback_data="todas")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 ¡Hola! Selecciona tu carrera para consultar las vacantes disponibles de residencia:",
        reply_markup=reply_markup
    )

# 3. Manejador de clics en los botones
async def responder_criterio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Confirmar recepción del clic

    carrera_seleccionada = query.data
    await query.edit_message_text(text=f"🔍 Buscando residencias para: *{carrera_seleccionada.upper()}*...", parse_mode="Markdown")

    vacantes = buscar_vacantes_por_carrera(carrera_seleccionada)

    if not vacantes:
        await query.message.reply_text("❌ No se encontraron vacantes específicas para este criterio por el momento.")
        return

    # Enviar máximo 5 vacantes como resultado
    for v in vacantes[:5]:
        mensaje = (
            f"🏢 *Empresa:* {v['empresa']}\n"
            f"📝 *Detalles:* {v['descripcion']}\n\n"
            f"🔗 [Abrir Portal de Residencias]({URL})"
        )
        await query.message.reply_text(mensaje, parse_mode="Markdown")

# 4. Configuración principal del bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Registrar comandos y listeners
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("carrera", start))
    app.add_handler(CallbackQueryHandler(responder_criterio))

    print("🤖 Bot interactivo iniciado. Presiona Ctrl+C para detener.")
    app.run_polling()

if __name__ == "__main__":
    main()
