import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

telegram_token = os.environ.get("TELEGRAM_TOKEN")
port = int(os.environ.get("PORT", 5000))
updater = Updater(telegram_token)

updater.start_webhook(listen="0.0.0.0", port=port, url_path=telegram_token)
updater.bot.setWebhook("https://alelo-bot.herokuapp.com/" + telegram_token)
r = redis.StrictRedis(host=os.environ.get('REDIS_URL'), db=0)

def start(bot, update):
    update.message.reply_text('Hi!')

def amount_help(bot, update):
    helps = int(r.get('help_count'))
    helps += 1
    r.set('helps', helps)

def help(bot, update):
    update.message.reply_text('Help!')


dp = updater.dispatcher

# on different commands - answer in Telegram
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler("c_help", amount_help))

updater.idle()