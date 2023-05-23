import telebot
from outputformatter import formoutput
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from kudagogetparams import GeoParams
from kudagogetter import getevents

bot = telebot.TeleBot("6010442984:AAEbdVOd2cG2wazpJoxnv2Ck0pKMdqkgU_8")


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btnevent = types.KeyboardButton("Найти мероприятия")
    btngeoevent = types.KeyboardButton("Найти мероприятия рядом", request_location=True)
    markup.add(btnevent, btngeoevent)
    bot.send_message(message.chat.id,
                     "Здравствуйте, {0.first_name}!\nВыберите опцию:".format(message.from_user, bot.get_me()),
                     reply_markup=markup)


@bot.message_handler(content_types=['location'])
def location(m):
    if m.location is not None:
        bot.send_message(m.chat.id,
                         "Ищем...",
                         reply_markup=None)
        lon = m.location.longitude
        lat = m.location.latitude
        userloc = GeoParams(lon, lat)
        pack = getevents(geoparams=userloc)
        msg = formoutput(pack)

        bot.send_message(m.chat.id,
                         msg)

    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btnrestart = types.KeyboardButton("/start")
        markup.add(btnrestart)
        bot.send_message(m.chat.id,
                         "При получении геолокации произошла непредвиденная ошибка!\nПожалуйста, перезапустите бота при помощи\nкоманды /start",
                         reply_markup=markup)


@bot.message_handler(content_types=['text'])
def txt_handler(m):
    if m.text == "Найти мероприятия":
        calendar, step = DetailedTelegramCalendar().build()
        bot.send_message(m.chat.id,
                         f"Выберите {LSTEP[step]}:",
                         reply_markup=calendar)
    else:
        bot.send_message(m.chat.id, "Неизвестная команда!", reply_markup=None)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}:",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text("Ищем...",
                              c.message.chat.id,
                              c.message.message_id)
        resdate = result.strftime("%Y-%m-%d")
        pack = getevents(date=resdate)
        msg = formoutput(pack)

        bot.edit_message_text(msg,
                              c.message.chat.id,
                              c.message.message_id)

bot.polling(none_stop=True, interval=0)