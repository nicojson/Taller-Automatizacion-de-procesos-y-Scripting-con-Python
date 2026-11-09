import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# --- CONFIGURACIÓN DE CREDENCIALES Y URL ---
TOKEN = "TU_TOKEN_DE_BOTFATHER"  # Reemplazar con el token de BotFather
CHAT_ID = "TU_CHAT_ID"           # Reemplazar con el Chat ID obtenido
URL = "https://sii.celaya.tecnm.mx/residencias-publicas/y9sXXxE9JMKXRonyeRBiDRyPKbIKIL4pPUXqjGOTYGL6JQ"

async def probar_bot_tecnm():
    print("🔍 Conectando con el portal del TecNM Celaya...")
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(URL, headers=headers)
        if res.status_code != 200:
            print(f"❌ Error al acceder a la página web (Código de estado: {res.status_code}).")
            return
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return

    soup = BeautifulSoup(res.text, "html.parser")
    articulos = soup.find_all("article")
    print(f"✅ Se encontraron {len(articulos)} vacantes en la primera página.\n")

    bot = Bot(token=TOKEN)
    
    # Enviar solo las primeras 3 vacantes como prueba inicial
    for art in articulos[:3]:
        empresa = art.find("h5").get_text(strip=True) if art.find("h5") else "Empresa N/A"
        categoria = art.find("small").get_text(strip=True) if art.find("small") else "Área N/A"
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

if __name__ == "__main__":
    # Punto de entrada estándar de Python para código asíncrono
    asyncio.run(probar_bot_tecnm())
