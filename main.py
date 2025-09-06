import os, logging
from sys import argv
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, User
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler
from datetime import datetime

from database import Database

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

NAME, TYPE, DATE, TIME = range(4)

HELP_MESSAGE = '''
Welcome to Party updates.

Use the following commands to get around:
/help - See this help message
/register - Register your account to start using the bot
/search - Search for Events happening around you
/newevent - create an event 
/events - see your upcoming events
/edit - edit your event
/delete - delete your event
'''

database: Database

def check_user(user: User | None, context: ContextTypes.DEFAULT_TYPE):
    if user is None:
        return None
    dbuser = database.readone("SELECT id, username FROM users WHERE username = ?", [user.username])
    return dbuser

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to Party updates!")
        return
    
    database_user = database.readone(f"SELECT * FROM users WHERE username='{user.username}'")
    if database_user is None:
        database.insertone("INSERT INTO users (username, userId, createdAt) VALUES (?, ?, ?)", (user.username, user.id, datetime.now()))
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to Party updates!")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_MESSAGE)
    
async def newevent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dbuser = check_user(update.effective_user, context)
    if dbuser is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You are not registered")
        return
    
    # reply_keyboard = []
    await update.message.reply_text(
        "What is the name of the event you are trying to publicize?",
        # reply_markup=ReplyKeyboardMarkup(
        #     reply_keyboard, one_time_keyboard=True
        # ),
    )
    
    return NAME

async def eventname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    logger.info("Event name: %s", name)
    
    context.chat_data['event_name'] = name
    
    # await update.message.reply_text("Cool! Saved. Now what is the type of event? (e.g., party, meeting, etc.)")
    reply_keyboard = [["Party", "Meeting", "Concert"], ["Workshop", "Other"]]
    await update.message.reply_text(
        "Cool! Saved. Now what is the type of event?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    
    return TYPE
    
async def eventtype(update: Update, context: ContextTypes.DEFAULT_TYPE):
    type = update.message.text
    logger.info("Event type: %s", type)
    
    if 'event_name' not in context.chat_data:
        await update.message.reply_text("Please provide an event name first.")
        return NAME
    
    event_name = context.chat_data['event_name']
    
    await update.message.reply_text(f"Event '{event_name}' of type '{type}' has been saved!") 
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main():
    token = os.environ.get('BOT_TOKEN')
    if not token or token == "":
        logging.error("Unable to retrieve bot token from environment. Add BOT_TOKEN to your environment.")
        exit(1)
    
    app = ApplicationBuilder().token(token).build()
    
    # Handlers
    start_handler=CommandHandler('start', start)
    
    app.add_handler(start_handler)
    app.add_handler(CommandHandler('help', help))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('newevent', newevent)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, eventname)],
            TYPE: [MessageHandler(filters.Regex("^()$"), eventtype)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    ))
        
    app.run_polling()

if __name__ == "__main__":
    load_dotenv(".env")
    database = Database()
    
    if len(argv) > 2:
        if argv[1] == "migrations:show":
            database.get_migrations()
        elif argv[1] == "migrations:run":
            database.run_migrations()
        elif argv[1] == "migrations:revert":
            database.revert_migrations(int(argv[2] if len(argv) == 3 else 1))
    else:
        main()