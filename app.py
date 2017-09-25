import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import redis
import requests
from io import BytesIO


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

telegram_token = os.environ.get("TELEGRAM_TOKEN")
port = int(os.environ.get("PORT", 5000))
updater = Updater(telegram_token)

updater.start_webhook(listen="0.0.0.0", port=port, url_path=telegram_token)
updater.bot.setWebhook("https://alelo-bot.herokuapp.com/" + telegram_token)
r = redis.from_url(os.environ.get("REDIS_URL"))
sess = {}

def start(bot, update):
    update.message.reply_text('Bem Vindo, por favor envie o seu token utilizando o comando de exemplo: /meu_alelo abcd1234')

def set_card_token(bot, update, args):
    token = args[0]
    user_id = update.message.from_user.id
    key = '{}_card_token'.format(user_id)
    r.set(key, token)
    update.message.reply_text('O token salvo.')

def get_card_token(bot, update):
    user_id = update.message.from_user.id
    key = '{}_card_token'.format(user_id)
    token = r.get(key).decode('utf-8')
    update.message.reply_text('O seu token salvo: {}'.format(str(token)))

def solve(bot, update):
    user_id = update.message.from_user.id
    sess[user_id] = requests.Session()
    res = sess[user_id].get('https://www.meualelo.com.br/inst/images/captcha.jpg', stream=True)
    res.raw.decode_content = True
    update.message.reply_photo(photo=res.raw, force_reply=True)

def session(bot, update, args):
    user_id = update.message.from_user.id
    data = {'txtCartao1': '5067542566047015', 'captcha': args[0]}
    res = sess[user_id].post('https://www.meualelo.com.br/SaldoExtratoValidacaoServlet', data=data)
    token = res.text.split('https://www.cartoesbeneficio.com.br/inst/SaldoExtratoAleloFiltro.jsp?ticket=')[1].split("'")[0]
    print(res.text)
    print(token)
    # update.message.reply_text('O seu token salvo: {}'.format(str(token)))

def balance(bot, update):
    user_id = update.message.from_user.id
    key = '{}_card_token'.format(user_id)
    token = r.get(key).decode('utf-8')
    response = requests.get('https://www.cartoesbeneficio.com.br/inst/convivencia/SaldoExtratoAlelo.jsp?ticket={}&primeiroAcesso=S&origem=Alelo'.format(token))
    balance = response.text.split('<span style="color: #008060;">')[1].split('</span>')[0]
    update.message.reply_text('Seu saldo: R$ {}'.format(str(balance)))


def help(bot, update):
    update.message.reply_text('Help!')


dispatcher = updater.dispatcher
commands = [
    CommandHandler("start", start),
    CommandHandler("meu_alelo", set_card_token, pass_args=True),
    CommandHandler("saldo", balance),
    CommandHandler("solve", solve),
    CommandHandler("session", session, pass_args=True)
]
for cmd in commands:
    dispatcher.add_handler(cmd)

updater.idle()