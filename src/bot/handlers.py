from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.utils import load_messages_for_bot, load_prompt, get_image_path
from src.openapi_client import OpenAiClient
from src.bot.messages import gpt_mode_response, talk_mode_response, quiz_mode_response
import logging


openai_client = OpenAiClient()


async def start(update: Update, context: ContextTypes):
    text = load_messages_for_bot("main")
    image_path = get_image_path("main")

    with open(image_path, 'rb') as photo:
        await update.message.reply_photo(photo=photo, caption=text, parse_mode='Markdown')


async def random_fact(update: Update, context: ContextTypes):
    text = load_messages_for_bot("random")
    prompt = load_prompt("random")
    image_path = get_image_path("random")

    keyboard = [
        [InlineKeyboardButton("Хочу ще факт", callback_data='random_again')],
        [InlineKeyboardButton("Закінчити", callback_data='finish')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        gpt_response = await openai_client.ask("", prompt)

        with open(image_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"{text}\n\n{gpt_response}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    except Exception as e:
        logging.error(f"Error in random_fact: {e}")
        await update.message.reply_text("Вибачте, сталася помилка. Спробуйте пізніше.")


async def gpt_interface(update: Update, context: ContextTypes):
    text = load_messages_for_bot("gpt")
    image_path = get_image_path("gpt")

    context.user_data['mode'] = 'gpt'

    with open(image_path, 'rb') as photo:
        await update.message.reply_photo(photo=photo, caption=text, parse_mode='Markdown')


async def talk_with_personality(update: Update, context: ContextTypes):
    text = load_messages_for_bot("talk")
    image_path = get_image_path("talk")

    keyboard = [
        [InlineKeyboardButton("Курт Кобейн", callback_data='talk_cobain')],
        [InlineKeyboardButton("Стівен Хокінг", callback_data='talk_hawking')],
        [InlineKeyboardButton("Фрідріх Ніцше", callback_data='talk_nietzsche')],
        [InlineKeyboardButton("Фредді Мерк'юрі", callback_data='talk_queen')],
        [InlineKeyboardButton("Дж.Р.Р. Толкін", callback_data='talk_tolkien')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open(image_path, 'rb') as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )


async def quiz_game(update: Update, context: ContextTypes):
    text = load_messages_for_bot("quiz")
    image_path = get_image_path("quiz")

    keyboard = [
        [InlineKeyboardButton("Історія", callback_data='quiz_history')],
        [InlineKeyboardButton("Наука", callback_data='quiz_science')],
        [InlineKeyboardButton("Мистецтво", callback_data='quiz_art')],
        [InlineKeyboardButton("Спорт", callback_data='quiz_sport')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open(image_path, 'rb') as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )


async def handle_text_messages(update: Update, context: ContextTypes):
    user_mode = context.user_data.get('mode', '')
    user_text = update.message.text

    if user_mode == 'gpt':
        await gpt_mode_response(openai_client, user_text, update)

    elif user_mode.startswith('talk_'):
        await talk_mode_response(openai_client,update, context)

    elif user_mode.startswith('quiz_'):
        await quiz_mode_response(openai_client, update,context)

async def handle_callback(update: Update, context: ContextTypes):
    query = update.callback_query
    await query.answer()

    if query.data == 'random_again':
        prompt = load_prompt("random")
        try:
            gpt_response = await openai_client.ask("", prompt)

            keyboard = [
                [InlineKeyboardButton("Хочу ще факт", callback_data='random_again')],
                [InlineKeyboardButton("Закінчити", callback_data='finish')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_caption(
                caption=f"{load_messages_for_bot('random')}\n\n{gpt_response}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logging.error(f"Error in random_again: {e}")
            await query.edit_message_caption("Вибачте, сталася помилка. Спробуйте пізніше.")

    elif query.data == 'finish':
        context.user_data.clear()
        await start(update, context)

    elif query.data.startswith('talk_'):
        personality = query.data.split('_')[1]
        context.user_data['mode'] = query.data

        personality_images = {
            'cobain': 'talk_cobain',
            'hawking': 'talk_hawking',
            'nietzsche': 'talk_nietzsche',
            'queen': 'talk_queen',
            'tolkien': 'talk_tolkien'
        }

        image_path = get_image_path(personality_images[personality])

        keyboard = [[InlineKeyboardButton("Закінчити", callback_data='finish')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open(image_path, 'rb') as photo:
            await query.message.reply_photo(
                photo=photo,
                caption="Можете почати розмову! Напишіть ваше повідомлення.",
                reply_markup=reply_markup
            )

    elif query.data.startswith('quiz_'):
        if query.data == 'quiz_change_topic':
            await quiz_game(update, context)
            return

        topic = query.data.split('_')[1]
        context.user_data['mode'] = query.data

        if 'score' not in context.user_data:
            context.user_data['score'] = 0

        topic_prompts = {
            'history': 'Створи одне цікаве питання з історії з 4 варіантами відповідей. Формат: Питання? A) ... B) ... C) ... D) ...',
            'science': 'Створи одне цікаве питання з науки з 4 варіантами відповідей. Формат: Питання? A) ... B) ... C) ... D) ...',
            'art': 'Створи одне цікаве питання з мистецтва з 4 варіантами відповідей. Формат: Питання? A) ... B) ... C) ... D) ...',
            'sport': 'Створи одне цікаве питання зі спорту з 4 варіантами відповідей. Формат: Питання? A) ... B) ... C) ... D) ...'
        }

        try:
            gpt_response = await openai_client.ask(topic_prompts[topic], load_prompt("quiz"))
            context.user_data['quiz_question'] = gpt_response

            await query.edit_message_caption(
                caption=f"{gpt_response}\n\nНапишіть вашу відповідь (A, B, C або D):"
            )
        except Exception as e:
            logging.error(f"Error in quiz: {e}")
            await query.edit_message_caption("Вибачте, сталася помилка. Спробуйте пізніше.")
