import telebot
from telebot import types

bot = telebot.TeleBot('1618328988:AAGixBfniXGhhSkusYPmTdpaoLr4EPqjZps')


# ---------------------------------------


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Нужна")
    btn2 = types.KeyboardButton("Нет", )
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Тебе не нужна помощь полиции?".format(message.from_user),
                     reply_markup=markup)

    btn3 = types.KeyboardButton("Нет")


# ---------------------------------------------------------------------------------------------------------------------------
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if (message.text == "Нужна"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("112")
        btn2 = types.KeyboardButton("Мой участковый")
        btn3 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, "Что вас интересует?", reply_markup=markup)

    if (message.text == "Нет"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)  # недодел(
        btn1 = types.KeyboardButton("Не знаю куда")
        btn2 = types.KeyboardButton("Знаю куда")
        btn3 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, "Вы хотите уйти, но не знаете куда?", reply_markup=markup)

    if (message.text == "112"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("112")
        btn2 = types.KeyboardButton("Мой участковый")
        btn3 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id,
                         "Если нужна срочная помощь наберите 112 или номер интересующие вас службы спасения!!",
                         reply_markup=markup)  # break

    if (message.text == "Мой участковый"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("112")
        btn2 = types.KeyboardButton("Мой участковый")
        btn3 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, "https://мвд.рф/district?ysclid=l8oiafifrx988880338",
                         reply_markup=markup)
        # --------------------------------------------- 2 СТУПЕНЬ-------------------------------------------------------------------------------

    if (message.text == "Не знаю куда"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("С ребёнком")
        btn2 = types.KeyboardButton("Без ребёнка")
        btn3 = types.KeyboardButton("Позвонить")
        btn4 = types.KeyboardButton("Назад")

        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.from_user.id, "Вы с ребёнком?", reply_markup=markup)

    if (message.text == "С ребёнком"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        bot.send_message(message.from_user.id,
                         "Позвоните на номер +7(4912)76-00-53 или перейдите по ссылке - https://vk.com/kcsonsemya62?ysclid=l8ojdanhg723759718", )

    if (message.text == "Без ребёнка"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1, )
        bot.send_message(message.from_user.id,
                         "https://vk.com/club204172284?ysclid=l8ojmcl2bx508283717 (Кризисный центр поддержки женщин <<Ангел>>)  или  https://vk.com/kcsonsemya62?ysclid=l8ojdanhg723759718(ГБУ РО КЦСОН Семья)", )

    if (message.text == "Позвонить"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1, )
        bot.send_message(message.from_user.id,
                         "+7-(906)-546-47-77 а так же https://vk.com/club204172284?ysclid=l8ojmcl2bx508283717(Кризисный центр поддержки женщин <<Ангел>>). Можете попробовать +7(4912)76-00-53 и https://vk.com/kcsonsemya62?ysclid=l8ojdanhg723759718 (ГБУ РО КЦСОН Семья)", )

    if (message.text == "Знаю куда"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("Помощь психолога")
        btn2 = types.KeyboardButton("Помощь юриста")
        btn3 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, "Вам нужна помощь психолога или юриста?", reply_markup=markup)

    if (message.text == "Помощь психолога"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("Нужна")
        btn2 = types.KeyboardButton("Не требуется")
        btn3 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id,
                         "Позвоните на номер +7(4912)76-00-53 или перейдите по ссылке - https://vk.com/kcsonsemya62?ysclid=l8ojdanhg723759718 (ГБУ РО КЦСОН Семья)", )

    if (message.text == "Помощь юриста"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("Нужна")
        btn2 = types.KeyboardButton("Не требуеться")
        btn3 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, "https://vk.com/lawyercom?ysclid=l8ok6w9col472168688", )

    if (message.text == "Назад"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Нужна")
        btn2 = types.KeyboardButton("Нет", )
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id,
                         text="Привет, {0.first_name}! Тебе не нужна помощь полиции?".format(message.from_user),
                         reply_markup=markup)


bot.infinity_polling(none_stop=True)
