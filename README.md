# С апреля 2017 скрипт проверки не работает, т.к. был изменён принцип записи

# FinlandVisaScheduleBot
Consulate of Finland status checker + telegram bot-announcer

Скрипт для мониторинга консульства Финляндии (возможность записи открывается раз в сутки на одну минуту в случайное время).

1. telegram-модуль: ждёт подписок/отписок, хранит chat_id в редисе, имеет публичный метод бродкаста сообщения;
2. tor-модуль: в конструкторе получает порт и запускает tor на этом порту, при обнулении ссылки на объект убивает процесс тора;
3. selenium-модуль: можно запускать N инстансов, каждый инстанс создаёт тор на новом порту и начинает бесконечный цикл проверок через тор, при успешной проверке происходит паблиш в редис сообщения;
4. redis-subscribe-модуль: подписывается на редис, получает сообщение о результате проверки; если статус сменился и не менялся уже более 5 секунд, то считаем, что он действительно сменился — запускаем бродкаст сообщения и обнуляем таймер смены статуса.

TODO: 
разобраться с жаваскрипт-колбеком на комбобоксе и вместо тяжёлого selenium'а слать прямые запросы
