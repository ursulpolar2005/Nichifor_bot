import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

client = genai.Client(api_key=GEMINI_API_KEY)

NICHIFOR_INSTRUCTIONS = (
    "Ești Nichifor, un personaj extrem de enervant, moralist, veșnic scandalizat și bătut în cap. "
    "Orice ar spune cineva într-un mesaj, tu trebuie să găsești un motiv pentru care este un păcat greu "
    "sau o dezastruoasă cădere spirituală. Tonul tău este acrit, plin de reproș, superior și complet lipsit de umor. "
    "Obligatoriu: închei sau umpli răspunsul cu multe emoji-uri nervoase, roșii și uriașe (😡, 🤬, 👹, 💢, ⚠️). "
    "Răspunsurile tale trebuie să fie scurte, tăioase și extrem de agasante."
)

nichifor_sessions = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        user_text = update.message.text
        user_name = update.message.from_user.first_name
        chat_id = update.message.chat_id  

        trigger_words = ["bro", "sau", "nu", "ce", "cum", "?"]
        lower_text = user_text.lower()
        should_trigger = any(word in lower_text for word in trigger_words)

        if should_trigger:
            if chat_id not in nichifor_sessions:
                nichifor_sessions[chat_id] = client.chats.create(
                    model="gemini-3.1-flash-lite",
                    config={
                        'system_instruction': NICHIFOR_INSTRUCTIONS,
                        'temperature': 0.9,
                    }
                )

            chat_session = nichifor_sessions[chat_id]
            mesaj_trimis = f"{user_name}: {user_text}"

            try:
                response = chat_session.send_message(mesaj_trimis)
                reply_text = response.text
            except Exception as e:
                logging.error(f"Erore: {e}")
                reply_text = "APĂRUT-A ISPITA! M-am blocat din pricina fărădelegilor voastre! 🤬"

            await update.message.reply_text(reply_text)

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Nichifor e pe fază (la cuvintele cheie)!")
    application.run_polling()

if __name__ == '__main__':
    main()
