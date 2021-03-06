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
    update.message.reply_text('Bem vindo!')
    update.message.reply_text('O meu objetivo é consultar o saldo do seu vale-refeicao Alelo, sem voce precisar baixar o app ;)')
    update.message.reply_text('Me envie o numero do seu vale-refeicao utilizando o comando /meu_alelo 999111777222')

def meu_alelo(bot, update, args):
    user_id = update.message.from_user.id
    sess[user_id] = (requests.Session(), args[0])
    res = sess[user_id][0].get('https://www.meualelo.com.br/inst/images/captcha.jpg', stream=True)
    res.raw.decode_content = True
    update.message.reply_photo(photo=res.raw, force_reply=True)
    update.message.reply_text('Agora me informe as letras e numeros da imagem acima utilizando o comando /resposta a1b2')

def session(bot, update, args):
    user_id = update.message.from_user.id
    data = {'txtCartao1': sess[user_id][1], 'captcha': args[0]}
    res = sess[user_id][0].post('https://www.meualelo.com.br/SaldoExtratoValidacaoServlet', data=data)
    token = res.text.split('https://www.cartoesbeneficio.com.br/inst/SaldoExtratoAleloFiltro.jsp?ticket=')[1].split("'")[0]
    user_id = update.message.from_user.id
    key = '{}_card_token'.format(user_id)
    r.set(key, token)
    update.message.reply_text('Tudo pronto! Toda vez que quiser consultar o seu saldo eh so me enviar o comando /saldo')
    del sess[user_id]

def balance(bot, update):
    user_id = update.message.from_user.id
    key = '{}_card_token'.format(user_id)
    token = r.get(key).decode('utf-8')
    response = requests.get('https://www.cartoesbeneficio.com.br/inst/convivencia/SaldoExtratoAlelo.jsp?ticket={}&primeiroAcesso=S&origem=Alelo'.format(token))
    balance = response.text.split('<span style="color: #008060;">')[1].split('</span>')[0]
    update.message.reply_text('Seu saldo: {}'.format(str(balance)))


dispatcher = updater.dispatcher
commands = [
    CommandHandler("start", start),
    CommandHandler("saldo", balance),
    CommandHandler("meu_alelo", meu_alelo, pass_args=True),
    CommandHandler("resposta", session, pass_args=True)
]
for cmd in commands:
    dispatcher.add_handler(cmd)

updater.idle()