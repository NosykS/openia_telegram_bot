from src.utils import load_prompt
from src.openapi_client import OpenAiClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import logging


async def gpt_mode_response(openai_client: OpenAiClient, user_text: str, update: Update) -> None:
    prompt = load_prompt("gpt")
    try:
        gpt_response = await openai_client.ask(user_text, prompt)
        await update.message.reply_text(gpt_response)
    except Exception as e:
        logging.error(f"Error in gpt mode: {e}")
        await update.message.reply_text("Вибачте, сталася помилка. Спробуйте пізніше.")

async def talk_mode_response(openai_client: OpenAiClient, update: Update, context=None) -> None:
    user_mode = context.user_data.get('mode', '')
    user_text = update.message.text
    personality = user_mode.split('_')[1]
    prompt = load_prompt(f"talk_{personality}")

    keyboard = [[InlineKeyboardButton("Закінчити", callback_data='finish')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        gpt_response = await openai_client.ask(user_text, prompt)
        await update.message.reply_text(gpt_response, reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Error in talk mode: {e}")
        await update.message.reply_text("Вибачте, сталася помилка. Спробуйте пізніше.")

async def quiz_mode_response(openai_client: OpenAiClient, update: Update, context=None) -> None:
    user_mode = context.user_data.get('mode', '')
    user_text = update.message.text
    topic = user_mode.split('_')[1]
    score = context.user_data.get('score', 0)

    if 'quiz_question' in context.user_data:
        try:
            check_prompt = f"Користувач відповів: '{user_text}' на питання: '{context.user_data['quiz_question']}'. Скажи чи правильна відповідь (так/ні) та дай коротке пояснення."
            gpt_response = await openai_client.ask(check_prompt,
                                                   "Ти експерт з квізів. Перевіряй відповіді користувачів.")

            is_correct = "так" in gpt_response.lower() or "правильн" in gpt_response.lower()
            if is_correct:
                context.user_data['score'] = score + 1

            current_score = context.user_data.get('score', 0)

            keyboard = [
                [InlineKeyboardButton("Ще питання", callback_data=f'quiz_{topic}')],
                [InlineKeyboardButton("Змінити тему", callback_data='quiz_change_topic')],
                [InlineKeyboardButton("Закінчити", callback_data='finish')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            response_text = f"{gpt_response}\n\nВаш рахунок: {current_score}"
            await update.message.reply_text(response_text, reply_markup=reply_markup)

            del context.user_data['quiz_question']
        except Exception as e:
            logging.error(f"Error in quiz mode: {e}")
            await update.message.reply_text("Вибачте, сталася помилка. Спробуйте пізніше.")
