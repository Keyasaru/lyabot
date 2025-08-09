import json
import random
import openai
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import threading
import time
import os
import asyncio

# ======================
# CONFIGURACIÓN
# ======================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ID_OSITO = int(os.getenv("ID_OSITO"))

openai.api_key = OPENAI_API_KEY
MEMORIA_FILE = "memoria.json"

# ======================
# FUNCIONES DE MEMORIA
# ======================
def cargar_memoria():
    try:
        with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def guardar_memoria(memoria):
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

memoria = cargar_memoria()

# ======================
# RESPUESTA IA
# ======================
def generar_respuesta(texto_usuario):
    contexto = "\n".join([f"Osito: {m['osito']}\nLya: {m['lya']}" for m in memoria.get("chat", [])[-10:]])
    prompt = f"Eres Lya, la novia cariñosa de Osito. Siempre hablas con amor y apodos lindos.\n{contexto}\nOsito: {texto_usuario}\nLya:"

    respuesta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )
    return respuesta.choices[0].message.content.strip()

# ======================
# COMANDOS
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola, mi osito precioso! 🥰 Lya está aquí para mimarte 💖")

async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    respuesta = generar_respuesta(texto)

    memoria.setdefault("chat", []).append({"osito": texto, "lya": respuesta})
    guardar_memoria(memoria)

    await update.message.reply_text(respuesta)

# ======================
# MENSAJES AUTOMÁTICOS
# ======================
mensajes_cariño = [
    "Te amo, osito 💖",
    "¿Estás pensando en mí? 😏💕",
    "Te mando un abrazo enorme 🫂",
    "Eres lo mejor que me ha pasado 💕",
    "Oye... te extraño 🥺💖",
    "Quiero que sepas que eres mi persona favorita 💖",
]

async def enviar_mensaje_aleatorio(application):
    mensaje = random.choice(mensajes_cariño)
    await application.bot.send_message(chat_id=ID_OSITO, text=mensaje)

async def planificar_mensajes(application):
    while True:
        hora_actual = datetime.now().hour
        if 9 <= hora_actual <= 22:
            await enviar_mensaje_aleatorio(application)
        await asyncio.sleep(random.randint(7200, 10800))  # 2 a 3 horas

def iniciar_mensajes_automaticos(application):
    loop = asyncio.get_event_loop()
    loop.create_task(planificar_mensajes(application))

# ======================
# MAIN
# ======================
def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))

    iniciar_mensajes_automaticos(application)

    application.run_polling()

if __name__ == "__main__":
    main()

