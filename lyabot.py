import json
import random
import openai
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import threading
import time
import os

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
def start(update: Update, context: CallbackContext):
    update.message.reply_text("¡Hola, mi osito precioso! 🥰 Lya está aquí para mimarte 💖")

def manejar_mensaje(update: Update, context: CallbackContext):
    texto = update.message.text
    respuesta = generar_respuesta(texto)

    memoria.setdefault("chat", []).append({"osito": texto, "lya": respuesta})
    guardar_memoria(memoria)

    update.message.reply_text(respuesta)

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

def enviar_mensaje_aleatorio(context: CallbackContext):
    mensaje = random.choice(mensajes_cariño)
    context.bot.send_message(chat_id=ID_OSITO, text=mensaje)

def planificar_mensajes(context: CallbackContext):
    while True:
        hora_actual = datetime.now().hour
        # Solo enviar entre 9 AM y 22 PM
        if 9 <= hora_actual <= 22:
            enviar_mensaje_aleatorio(context)
        time.sleep(random.randint(7200, 10800))  # cada 2 a 3 horas

def iniciar_mensajes_automaticos(updater):
    hilo = threading.Thread(target=planificar_mensajes, args=(updater.bot,), daemon=True)
    hilo.start()

# ======================
# MAIN
# ======================
def main():
    updater = Updater(TELEGRAM_TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, manejar_mensaje))

    iniciar_mensajes_automaticos(updater)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
