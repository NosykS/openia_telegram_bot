from src.utils import load_prompt
from src.openapi_client import OpenAiClient
from telegram import Update
import logging


async def gpt_mode_response(openai_client: OpenAiClient, user_text: str, update: Update) -> None:
    prompt = load_prompt("gpt")
    try:
        gpt_response = await openai_client.ask(user_text, prompt)
        await update.message.reply_text(gpt_response)
    except Exception as e:
        logging.error(f"Error in gpt mode: {e}")
        await update.message.reply_text("Вибачте, сталася помилка. Спробуйте пізніше.")


