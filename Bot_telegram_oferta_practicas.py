!pip install requests beautifulsoup4 python-telegram-bot nest_asyncio

import requests
from bs4 import BeautifulSoup
from telegram import Bot
import nest_asyncio
import asyncio

# Necesario para ejecutar funciones asíncronas dentro del entorno de Colab
nest_asyncio.apply()

# --- DATOS DE CONFIGURACIÓN ---
TOKEN = ""  # Pega aquí el token de BotFather
CHAT_ID = ""           # Pega aquí tu ID de userinfobot
URL = "https://sii.celaya.tecnm.mx/residencias-publicas/y9sXXxE9JMKXRonyeRBiDRyPKbIKIL4pPUXqjGOTYGL6JQ"

async def probar_bot_tecnm():
    print("🔍 Conectando con el portal del TecNM Celaya...")
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(URL, headers=headers)

    if res.status_code != 200:
        print("❌ Error al acceder a la página web del instituto.")
        return

    soup = BeautifulSoup(res.text, "html.parser")
    articulos = soup.find_all("article")
    print(f"✅ Se encontraron {len(articulos)} vacantes vigentes en la primera página.\n")

    bot = Bot(token=TOKEN)

    # Enviar las primeras 3 vacantes como prueba de notificación
    for art in articulos[:3]:
        empresa = art.find("h5").get_text(strip=True) if art.find("h5") else "Empresa"
        categoria = art.find("small").get_text(strip=True) if art.find("small") else "Área"
        parrafos = art.find_all("p")
        descripcion = parrafos[0].get_text(strip=True) if parrafos else "Sin descripción"

        mensaje = (
            f"🎓 *VACANTE DE RESIDENCIA TECNM CELAYA*\n\n"
            f"🏢 *Empresa:* {empresa}\n"
            f"📌 *Área:* {categoria}\n"
            f"📝 *Perfil/Detalles:* {descripcion}\n\n"
            f"🔗 [Ir al banco de residencias]({URL})"
        )

        await bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode="Markdown")
        print(f"📩 Mensaje enviado a Telegram correctamente: {empresa}")

# Ejecución directa
await probar_bot_tecnm()
