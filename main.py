import os
import logging
import dotenv
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, InlineQueryHandler

from uuid import uuid4

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, talk to me!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
 
async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=str(uuid4()),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    results.append(
        InlineQueryResultArticle(
            id=str(uuid4()),
            title='Search',
            input_message_content=InputTextMessageContent("What are you searching for werey?")
        )
    )
    
    print(results)
    
    await context.bot.answer_inline_query(update.inline_query.id, results)

if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    
    app = ApplicationBuilder().token(str(os.environ.get('BOT_TOKEN'))).build()
    
    start_handler = CommandHandler('start', start)
    caps_handler = CommandHandler('caps', caps)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    inline_caps_handler = InlineQueryHandler(inline_caps)
   
    app.add_handler(start_handler)
    app.add_handler(caps_handler)
    app.add_handler(echo_handler)
    app.add_handler(inline_caps_handler)
    
    app.run_polling()