from src.config import TG_BOT_API_KEY
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from src.bot import handlers
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = ApplicationBuilder().token(TG_BOT_API_KEY).build()

app.add_handler(CommandHandler("start", handlers.start))
app.add_handler(CommandHandler("random", handlers.random_fact))
app.add_handler(CommandHandler("gpt", handlers.gpt_interface))
app.add_handler(CommandHandler("talk", handlers.talk_with_personality))
app.add_handler(CommandHandler("quiz", handlers.quiz_game))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text_messages))
app.add_handler(CallbackQueryHandler(handlers.handle_callback))

app.run_polling()
