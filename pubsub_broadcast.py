#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
from FinlandVisaScheduleBot import FinlandVisaScheduleBot
import time

class FinlandVisaScheduleRedisSubscriber(object):
    redis_channel = 'finland_visa_schedule_bot_channel'
    bad_message = u'Доступные для записи даты отсутствуют'

    def __init__(self, redis_key, redis_host=None, redis_port=None):
        if not redis_host:
            redis_host = '127.0.0.1'
        if not redis_port:
            redis_port = 6379
        self.bot = FinlandVisaScheduleBot(redis_key, redis_host, redis_port)
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(self.redis_channel)

    def start_infinite_loop(self):
        prev_msg = self.bad_message
        ts_start = time.time()
        for message in self.pubsub.listen():
            ts_end = time.time()
            msg = message['data']
            if not isinstance(msg, str):
                print msg
                continue
            msg = msg.decode('utf-8')
            # подавляем возможный дребезг (до 5 секунд) возвращаемых значений
            # запустили таймер
            # пришло новое сообщение, инвертирующее статус:
            # если таймер натикал > 5с - бродкастнули, обнулили таймер
            if (prev_msg <> msg) and (ts_end - ts_start > 5):
                self.bot.broadcast(msg)
                ts_start = ts_end
                prev_msg = msg

if __name__ == '__main__':
    import time
    sub = FinlandVisaScheduleRedisSubscriber('finland_visa_schedule_bot_chat_id')
    while True:
        sub.start_infinite_loop()