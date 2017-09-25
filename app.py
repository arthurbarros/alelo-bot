import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import redis

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

telegram_token = os.environ.get("TELEGRAM_TOKEN")
port = int(os.environ.get("PORT", 5000))
updater = Updater(telegram_token)

updater.start_webhook(listen="0.0.0.0", port=port, url_path=telegram_token)
updater.bot.setWebhook("https://alelo-bot.herokuapp.com/" + telegram_token)
r = redis.from_url(os.environ.get("REDIS_URL"))

def start(bot, update):
    update.message.reply_text('Hi!')

def amount_help(bot, update):
    helps = r.get('help_count')
    helps = int(helps) if helps else 0
    helps += 1
    r.set('help_count', helps)
    update.message.reply_text(helps)

def help(bot, update):
    update.message.reply_text('Help!')


dispatcher = updater.dispatcher
commands = [
    CommandHandler("start", start),
    CommandHandler("help", help),
    CommandHandler("c_help", amount_help)
]
for cmd in commands:
    dispatcher.add_handler(cmd)

updater.idle()