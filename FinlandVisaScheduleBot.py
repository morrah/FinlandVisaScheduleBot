#!/usr/bin/python
# -*- coding: UTF-8 -*-
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler
import redis
import logging
import json

class FinlandVisaScheduleBot(object):

    TOKEN = 'USE:YOURS'

    def __init__(self, redis_key, redis_host=None, redis_port=None):
        self.redis_key = redis_key
        if not redis_host:
            redis_host = '127.0.0.1'
        if not redis_port:
            redis_port = 6379
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
        updater = Updater(self.TOKEN)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler('start', self.start))
        dp.add_handler(CommandHandler('help', self.start))
        dp.add_handler(CommandHandler('subscribe', self.subscribe))
        dp.add_handler(CommandHandler('unsubscribe', self.unsubscribe))
        dp.add_error_handler(self.error)
        updater.start_polling()

    def _get_chat_id_list(self):
        return self.redis.smembers(self.redis_key)

    def _add_chat_id(self, chat_id):
        self.redis.sadd(self.redis_key, chat_id)
    
    def _remove_chat_id(self, chat_id):
        self.redis.srem(self.redis_key, chat_id)

    def start(self, bot, update):
        custom_keyboard = [[ '/subscribe', '/unsubscribe' ]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.sendMessage(update.message.chat_id, text=u'/subscribe - подписка на оповещалку\n/unsubscribe - отписка', reply_markup=reply_markup)
        
    def subscribe(self, bot, update):
        chat_id = update.message.chat_id
        self._add_chat_id(chat_id)
        bot.sendMessage(update.message.chat_id, text=u'Подписано!')
    
    def unsubscribe(self, bot, update):
        chat_id = update.message.chat_id
        self._remove_chat_id(chat_id)
        bot.sendMessage(update.message.chat_id, text=u'Отписано!')
    
    def broadcast(self, msg):
        bot = telegram.Bot(token=self.TOKEN)
        print self._get_chat_id_list()
        for chat_id in self._get_chat_id_list():
            bot.sendMessage(chat_id, text=msg)
    
    def error(self, bot, update, error):
        logging.warn('Update "%s" caused error "%s"' % (update, error))