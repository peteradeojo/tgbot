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

if __name__ == "__main__":
    load_dotenv()
    database = Database()