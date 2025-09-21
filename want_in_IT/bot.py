#Импортирование библиотеки и модулей
from aiogram import Bot, types, Dispatcher, executor
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


#Токен(ключ) бота
bot = Bot(token="-")

dp = Dispatcher(bot)

#Старотовый хэндлер
@dp.message_handler(commands='start')
async def start_cmd(msg: types.Message):
    n = msg.from_user.full_name
    await msg.answer(f'Привет, {n}!')
    button1 = KeyboardButton('Мероприятия')
    button2 = KeyboardButton('Карьерные карты')
    button3 = KeyboardButton('Стажировочные площадки')
    button4 = KeyboardButton('Акселератор')
    button5 = KeyboardButton('/start')
    but = ReplyKeyboardMarkup(resize_keyboard=True)
    but.add(button1).insert(button2).add(button3).insert(button4).add(button5)
    inline_button = InlineKeyboardMarkup(raw_width=1)
    url_button = InlineKeyboardButton(text='Профград', url='https://deti.digital/')
    inline_button.add(url_button)
    await msg.reply('Так же у нас есть платформа для поддержки талантливых детей <Профград>', reply_markup=inline_button)
    inline_button1 = InlineKeyboardMarkup(raw_width=1)
    url_button1 = InlineKeyboardButton(text='Тест', url='https://myfreedom.by/test/proforientation')
    inline_button1.add(url_button1)
    await msg.answer('Ещё вы можете пройти  тест нажав на кнопку <Тест>', reply_markup=inline_button1)
    await msg.answer('Выберите раздел для ознакомления', reply_markup=but)

#Хэндлер с основным функционалом
@dp.message_handler(content_types="text")
async def event(msg: types.Message):
    if msg.text == "Мероприятия":
        # Раздел с кнопкой мероприятия, и дополнительными функциями
        january = InlineKeyboardButton(text="Январь🎄", callback_data='a1')
        february = InlineKeyboardButton(text="Февраль💧", callback_data="a2")
        mart = InlineKeyboardButton(text="Март☔", callback_data="a3")
        april = InlineKeyboardButton(text="Апрель🌦️", callback_data="a4")
        may = InlineKeyboardButton(text="Май🌸", callback_data="a5")
        june = InlineKeyboardButton(text="Июнь🐝", callback_data="a6")
        july = InlineKeyboardButton(text="Июль☀", callback_data="a7")
        august = InlineKeyboardButton(text="Август🌝", callback_data="a8")
        september = InlineKeyboardButton(text="Сентябрь🍁", callback_data="a9")
        october = InlineKeyboardButton(text="Октябрь🎃", callback_data="a0")
        november = InlineKeyboardButton(text="Ноябрь🌧️", callback_data="a!")
        december = InlineKeyboardButton(text="Декабрь❄", callback_data="a?")
        url = InlineKeyboardMarkup().add(january).insert(february).add(mart).insert(april).add(may).insert(june).add(july).insert(august).add(september).insert(october).add(november).insert(december)
        await msg.reply("Календарь мероприятий на 2023 год", reply_markup=url)
        #Колбэк хэндлер для инлайн клавиатуры
        @dp.callback_query_handler(lambda c: c.data and c.data.startswith('a'))
        async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
            code = callback_query.data[-1]
            if code.isdigit():
                code = int(code)
            if code == 1:
                await bot.send_message(callback_query.from_user.id, 'Январь\n1(вс) - \n2(пн) - \n3(вт) - \n4(ср) - '
                                                                    '\n5(чт) - \n6(пт) - \n7(сб) - \n8(вс) - \n9(пн) - '
                                                                    '\n10(вт) - \n11(ср) - \n12(чт) - \n13(пт) - '
                                                                    '\n14(сб) - \n15(вс) - \n16(пн) - \n17(вт) - '
                                                                    '\n18(ср) - \n19(чт) - \n20(пт) - \n21(сб) - '
                                                                    '\n22(вс) - \n23(пн) - \n24(вт) - \n25(ср) - '
                                                                    '\n26(чт) - \n27(пт) - \n28(сб) - \n29(вс) - '
                                                                    '\n30(пн) - \n31(вт) -')
            if code == 2:
                await bot.send_message(callback_query.from_user.id, 'Февраль\n1(ср) - \n2(чт) - \n3(пт) - \n4(сб) - '
                                                                    '\n5(вс) - \n6(пн) - \n7(вт) - \n8(ср) - \n9(чт) - '
                                                                    '\n10(пт) - \n11(сб) - \n12(вс) - \n13(пн) - '
                                                                    '\n14(вт) - \n15(ср) - \n16(чт) - \n17(пт) - '
                                                                    '\n18(сб) - \n19(вс) - \n20(пн) - \n21(вт) - '
                                                                    '\n22(ср) - \n23(чт) - \n24(пт) - \n25(сб) - '
                                                                    '\n26(вс) - \n27(пн) - \n28(вт) -')
            if code == 3:
                await bot.send_message(callback_query.from_user.id, 'Март\n1(ср) - \n2(чт) - \n3(пт) - \n4(сб) - '
                                                                    '\n5(вс) - \n6(пн) - \n7(вт) - \n8(ср) - \n9(чт) - '
                                                                    '\n10(пт) - \n11(сб) - \n12(вс) - \n13(пн) - '
                                                                    '\n14(вт) - \n15(ср) - \n16(чт) - \n17(пт) - '
                                                                    '\n18(сб) - \n19(вс) - \n20(пн) - \n21(вт) - '
                                                                    '\n22(ср) - \n23(чт) - \n24(пт) - \n25(сб) - '
                                                                    '\n26(вс) - \n27(пн) - \n28(вт) - \n29(ср) - '
                                                                    '\n30(чт) - \n31(пт) -')
            if code == 4:
                await bot.send_message(callback_query.from_user.id, 'Апрель\n1(сб) - \n2(вс) - \n3(пн) - \n4(вт) - '
                                                                    '\n5(ср) - \n6(чт) - \n7(пт) - \n8(сб) - \n9(вс) - '
                                                                    '\n10(пн) - \n11(вт) - \n12(ср) - \n13(чт) - '
                                                                    '\n14(пт) - \n15(сб) - \n16(вс) - \n17(пн) - '
                                                                    '\n18(вт) - \n19(ср) - \n20(чт) - \n21(пт) - '
                                                                    '\n22(сб) - \n23(вс) - \n24(пн) - \n25(вт) - '
                                                                    '\n26(ср) - \n27(чт) - \n28(пт) - \n29(сб) - '
                                                                    '\n30(вс) -')
            if code == 5:
                await bot.send_message(callback_query.from_user.id, 'Май\n1(пн) - \n2(вт) - \n3(ср) - \n4(чт) - '
                                                                    '\n5(пт) - \n6(сб) - \n7(вс) - \n8(пн) - \n9(вт) - '
                                                                    '\n10(ср) - \n11(чт) - \n12(пт) - \n13(сб) - '
                                                                    '\n14(вс) - \n15(пн) - \n16(вт) - \n17(ср) - '
                                                                    '\n18(чт) - \n19(пт) - \n20(сб) - \n21(вс) - '
                                                                    '\n22(пн) - \n23(вт) - \n24(ср) - \n25(чт) - '
                                                                    '\n26(пт) - \n27(сб) - \n28(вс) - \n29(пн) - '
                                                                    '\n30(вт) - \n31(ср) -')
            if code == 6:
                await bot.send_message(callback_query.from_user.id, 'Июнь\n1(чт) - \n2(пт) - \n3(сб) - \n4(вс) - '
                                                                    '\n5(пн) - \n6(вт) - \n7(ср) - \n8(чт) - \n9(пт) - '
                                                                    '\n10(сб) - \n11(вс) - \n12(пн) - \n13(вт) - '
                                                                    '\n14(ср) - \n15(чт) - \n16(пт) - \n17(сб) - '
                                                                    '\n18(вс) - \n19(пн) - \n20(вт) - \n21(ср) - '
                                                                    '\n22(чт) - \n23(пт) - \n24(сб) - \n25(вс) - '
                                                                    '\n26(пн) - \n27(вт) - \n28(ср) - \n29(чт) - '
                                                                    '\n30(пт) -')
            if code == 7:
                await bot.send_message(callback_query.from_user.id, 'Июль\n1(сб) - \n2(вс) - \n3(пн) - \n4(вт) - '
                                                                    '\n5(ср) - \n6(чт) - \n7(пт) - \n8(сб) - \n9(вт) - '
                                                                    '\n10(пн) - \n11(вт) - \n12(ср) - \n13(чт) - '
                                                                    '\n14(пт) - \n15(сб) - \n16(вс) - \n17(пн) - '
                                                                    '\n18(вт) - \n19(ср) - \n20(чт) - \n21(пт) - '
                                                                    '\n22(сб) - \n23(вс) - \n24(пн) - \n25(вс) - '
                                                                    '\n26(ср) - \n27(чт) - \n28(пт) - \n29(сб) - '
                                                                    '\n30(вс) - \n31(пн) -')
            if code == 8:
                await bot.send_message(callback_query.from_user.id, 'Август\n1(вт) - \n2(ср) - \n3(чт) - \n4(пт) - '
                                                                    '\n5(сб) - \n6(вс) - \n7(пн) - \n8(вт) - \n9(ср) - '
                                                                    '\n10(чт) - \n11(пт) - \n12(сб) - \n13(вс) - '
                                                                    '\n14(пн) - \n15(вт) - \n16(ср) - \n17(чт) - '
                                                                    '\n18(пт) - \n19(сб) - \n20(вс) - \n21(пн) - '
                                                                    '\n22(вт) - \n23(ср) - \n24(чт) - \n25(пт) - '
                                                                    '\n26(сб) - \n27(вс) - \n28(пн) - \n29(вт) - '
                                                                    '\n30(ср) - \n31(чт) -')
            if code == 9:
                await bot.send_message(callback_query.from_user.id, 'Сентябрь\n1(пт) - \n2(сб) - \n3(вс) - \n4(пн) - '
                                                                    '\n5(вт) - \n6(ср) - \n7(чт) - \n8(пт) - \n9(сб) - '
                                                                    '\n10(вс) - \n11(пн) - \n12(вт) - \n13(ср) - '
                                                                    '\n14(чт) - \n15(пт) - \n16(сб) - \n17(вс) - '
                                                                    '\n18(пн) - \n19(вт) - \n20(ср) - \n21(чт) - '
                                                                    '\n22(пт) - \n23(сб) - \n24(вс) - \n25(пн) - '
                                                                    '\n26(вт) - \n27(ср) - \n28(чт) - \n29(пт) - '
                                                                    '\n30(сб) - ')
            if code == 0:
                await bot.send_message(callback_query.from_user.id, 'Октябрь\n1(вс) - \n2(пн) - \n3(вт) - \n4(ср) - '
                                                                    '\n5(чт) - \n6(пт) - \n7(сб) - \n8(вс) - \n9(пн) - '
                                                                    '\n10(вт) - \n11(ср) - \n12(чт) - \n13(пт) - '
                                                                    '\n14(сб) - \n15(вс) - \n16(пн) - \n17(вт) - '
                                                                    '\n18(ср) - \n19(чт) - \n20(пт) - \n21(сб) - '
                                                                    '\n22(вс) - \n23(пн) - \n24(вт) - \n25(ср) - '
                                                                    '\n26(чт) - \n27(пт) - \n28(сб) - \n29(вс) - '
                                                                    '\n30(пн) - \n31(вт) -')
            if code == '!':
                await bot.send_message(callback_query.from_user.id, 'Ноябрь\n1(ср) - \n2(чт) - \n3(пт) - \n4(сб) - '
                                                                    '\n5(вс) - \n6(пн) - \n7(вт) - \n8(ср) - \n9(чт) - '
                                                                    '\n10(пт) - \n11(сб) - \n12(вс) - \n13(пн) - '
                                                                    '\n14(вт) - \n15(ср) - \n16(чт) - \n17(пт) - '
                                                                    '\n18(сб) - \n19(вс) - \n20(пн) - \n21(вт) - '
                                                                    '\n22(ср) - \n23(чт) - \n24(пт) - \n25(сб) - '
                                                                    '\n26(вс) - \n27(пн) - \n28(вт) - \n29(ср) - '
                                                                    '\n30(чт) - ')
            if code == "?":
                await bot.send_message(callback_query.from_user.id, 'Декабрь\n1(пт) - \n2(сб) - \n3(вс) - \n4(пн) - '
                                                                    '\n5(вт) - \n6(ср) - \n7(чт) - \n8(пт) - \n9(сб) - '
                                                                    '\n10(вс) - \n11(пн) - \n12(вт) - \n13(ср) - '
                                                                    '\n14(чт) - \n15(пт) - \n16(сб) - \n17(вс) - '
                                                                    '\n18(пн) - \n19(вт) - \n20(ср) - \n21(чт) - '
                                                                    '\n22(пт) - \n23(сб) - \n24(вс) - \n25(пн) - '
                                                                    '\n26(вт) - \n27(ср) - \n28(чт) - \n29(пт) - '
                                                                    '\n30(сб) - \n31(вс)')

    if msg.text == 'Акселератор':
        await msg.answer('Детский ИТ-акселератор\n\nДля детей от 14 до 18 лет\nСодействует появлению и увеличению числа успешных качественных стартап-команд, талантов, инноваторов на входе в инновационную экосистему национальной экономики.')
        await msg.answer('Что ждёт участников?\nДля того чтобы узнать обо всём подробнее и подать заявку в акселератор, перейдите по ссылке:\nhttps://digitalway62.ru/akselerator/ ')

    if msg.text == 'Стажировочные площадки':
        url_int_button_1 = InlineKeyboardMarkup(raw_width=1)
        url_int_button_2 = InlineKeyboardMarkup(raw_width=1)
        url_int_button_3 = InlineKeyboardMarkup(raw_width=1)
        url_int_button_4 = InlineKeyboardMarkup(raw_width=1)
        url_int_button_5 = InlineKeyboardMarkup(raw_width=1)
        url_int_button_6 = InlineKeyboardMarkup(raw_width=1)
        url_int_button_7 = InlineKeyboardMarkup(raw_width=1)
        url_int_button_8 = InlineKeyboardMarkup(raw_width=1)
        url_Button_is = InlineKeyboardButton(text='Экскурсия',
                                             url='https://digitalway62.ru/panorams/medical-center/index.html')
        url_Button_is_2 = InlineKeyboardButton(text='Экскурсия',
                                               url='https://digitalway62.ru/panorams/theatre/index.html')
        url_Button_is_3 = InlineKeyboardButton(text='Экскурсия', url='https://digitalway62.ru/panorams/kvantron/')
        url_Button_is_4 = InlineKeyboardButton(text='Экскурсия',
                                               url='https://digitalway62.ru/panorams/digital-region/index.html')
        url_Button_is_5 = InlineKeyboardButton(text='Экскурсия',
                                               url='https://digitalway62.ru/panorams/secure/index.html')
        url_Button_is_6 = InlineKeyboardButton(text='Экскурсия', url='http://tour.fotokino.pro/gorkylibrary/2020')
        url_Button_is_7 = InlineKeyboardButton(text='Экскурсия', url='http://digitalway62.ru/panorams/d-link/')
        url_Button_is_8 = InlineKeyboardButton(text='Экскурсия', url='https://digitalway62.ru/panorams/leadmachine/')
        url_int_button_1.add(url_Button_is)
        url_int_button_2.add(url_Button_is_2)
        url_int_button_3.add(url_Button_is_3)
        url_int_button_4.add(url_Button_is_4)
        url_int_button_5.add(url_Button_is_5)
        url_int_button_6.add(url_Button_is_6)
        url_int_button_7.add(url_Button_is_7)
        url_int_button_8.add(url_Button_is_8)
        button_1 = InlineKeyboardButton(text="РязГМУ имени академика И.П. Павлова", callback_data="rus1")
        button_2 = InlineKeyboardButton(text="Рязанский государственный областной театр Драмы", callback_data="rus2")
        button_3 = InlineKeyboardButton(text="Квантрон", callback_data="rus3")
        button_4 = InlineKeyboardButton(text="АНО Цифровой регион", callback_data="rus4")
        button_5 = InlineKeyboardButton(text="Группа компаний Центр комплексной безопасности информационных технологий",
                                        callback_data="rus5")
        button_6 = InlineKeyboardButton(text="Библиотека им. Горького", callback_data="rus6")
        button_7 = InlineKeyboardButton(text="D-Link", callback_data="rus7")
        button_8 = InlineKeyboardButton(text="Агентство интернет-маркетинга «Лидмашина»", callback_data="rus8")
        keyboard = InlineKeyboardMarkup().add(button_1).insert(button_2).add(button_3).insert(button_4).add(
            button_5).insert(button_6).add(button_7).insert(button_8)

        await msg.answer("Стажировочные площадки", reply_markup=keyboard)

        @dp.callback_query_handler(lambda c: c.data and c.data.startswith('rus'))
        async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
            code = callback_query.data[-1]
            if code.isdigit():
                code = int(code)
            if code == 1:
                await bot.send_message(callback_query.from_user.id, 'РязГМУ имени академика И.П. Павлова,'
                                                                    "РязГМУ имени академика И.П.Павлова. Рязанский государственный медицинский университет  имени академика И.П. Павлова – крупный профильный вуз, история которого начинается в 1943 году, "
                                                                    "когда на базе 3-го и 4-го Московских медицинских институтов был создан Московский медицинский институт Министерства здравоохранения РСФСР. "
                                                                    "Сегодня РязГМУ — это учебно-научно-лечебное учреждение с развитой материально-технической базой: сейчас университет располагает 16 учебно-лабораторными корпусами общей площадью 73 140 кв м,"
                                                                    "научно-клиническим центром, ботаническим садом, базой отдыха «Здоровье в поселке курортного типа Солотча». "

                                                                    "Адрес 390026 г. Рязань, ул. Высоковольтная, д. 9 "
                                                                    "Контактный номер +7(4912)97-18-18 "
                                                                    "E-mail: rzgmu@rzgmu.ru",
                                       reply_markup=url_int_button_1)
            if code == 2:
                await bot.send_message(callback_query.from_user.id, "Рязанский государственный областной театр Драмы"
                                                                    "Рязанский государственный Ордена «Знак Почета» областной театр драмы является одним "
                                                                    "из старейших в России, основан в 1787 году. Сегодня работая в сложных экономических условиях, "
                                                                    "театр живет полнокровной жизнью, выпуская новые спектакли, участвуя в различных фестивалях, "
                                                                    "старается сохранить и приумножить традиции великого русского искусства"
                                                                    " и одновременно идти в ногу со временем. "
                                                                    "Адрес 390023 г. Рязань, Театральная площадь, д. 7А, "
                                                                    "Контактный номер +7(4912)45-03-56 "
                                                                    "E-mail: rzndrama@yandex.ru	",
                                       reply_markup=url_int_button_2)
            if code == 3:
                await bot.send_message(callback_query.from_user.id,
                                       "Квантрон."" Компания ООО «Квантрон Групп» является резидентом Рязанского инновационного "
                                       "научнотехнического центра. В Группу входят компания «Квантрон» основанная в 2010 "
                                       "году и ООО «Сенсис» основанная в 2016 году. ООО «Квантрон» занимается научными "
                                       "исследованиями и разработками программно-аппаратных комплексов технического зрения"
                                       " и автоматизации, ООО «Сенсис» внедрением разработанных систем на предприятия и "
                                       "реверсивным инжинирингом. Также в Группу входит ООО «Рязанский инструментальный "
                                       "завод» основанный в 2016 году, который занимается разработкой и производством "
                                       "высокоэффективного режущего инструмента из твердого сплава для станков с ЧПУ. "
                                       "Адрес: 390000, г. Рязань, ул. Каширина, д. 1Б, офис 507 "
                                       "Контактный номер: +7(4912)770-775 "
                                       "E-mail: info@kvantron.com", reply_markup=url_int_button_3)
            if code == 4:
                await bot.send_message(callback_query.from_user.id,
                                       "АНО Цифровой регион. " "Автономная некоммерческая организация «Цифровой регион» является унитарной "
                                       "некоммерческой организацией, не имеющей членства, юридических лиц в целях предоставления услуг"
                                       "по разработке, внедрению, развитию и сопровождению цифровых технологий, развитию информационного общества,"
                                       "инновационной и научно-технической деятельности в Рязанской области, услуг в сфере образования. " "Адрес: 390000"
                                       "г. Рязань, ул. Каширина, д. 1Б, Контактный номер: +7(800)550-26-8 E-mail: mail@digitalr.ru",
                                       reply_markup=url_int_button_4)
            if code == 5:
                await bot.send_message(callback_query.from_user.id,
                                       "Группа компаний «Центр комплексной безопасности информационных технологий»"
                                       "Группа компаний «Центр комплексной безопасности информационных технологий» предоставляет полный"
                                       " перечень услуг в области защиты информации: создание информационных систем в защищенном "
                                       "исполнении, аттестацию информационных систем на соответствие требованиям по защите информации,"
                                       "защита и аттестация помещений, предназначенных для проведения конфиденциальных переговоров, "
                                       "в соответствии с требованиям по защите информации, а также обучение специалистов по одной из "
                                       "программ дополнительного профессионального образования в области информационной безопасности. "
                                       " Входящие в группу компаний юридические лица обладают лицензиями ФСТЭК России, ФСБ России, "
                                       "а также Министерства образования. Программы дополнительного образования имеют согласование с "
                                       "регуляторами в области информационной безопасности: ФСТЭК России, ФСБ России, а также МВК ГТ."
                                       "Адрес: 390010 г. Рязань, ул. Новикова-Прибоя, д. 10, Контактный номер: "
                                       "+7(4912)38-77-11" "E-mail: rcb@rcbrzn.ru", reply_markup=url_int_button_5)
            if code == 6:
                await bot.send_message(callback_query.from_user.id,
                                       "Библиотека им. Горького " "Государственное бюджетное учреждение культуры Рязанской области "
                                       "«Рязанская областная универсальная научная библиотека имени Горького» (РОУНБ) является главной "
                                       "библиотекой рязанского региона. Деятельность библиотеки осуществляется в соответствии с "
                                       "«Основами государственной культурной политики»,осударственной культурной политики на период до "
                                       "2030 года», задачами, определенными указом Президента РФ № 203 от 9 мая 2017 года "
                                       "«О стратегии развития информационного общества», Указом Президента Российской Федерации "
                                       "№ 204 от 7 мая 2018 года «О национальных целях и стратегических задачах развития Российской "
                                       "Федерации на период до 2024 года», " "национальным проектом «Культура», утвержденным "
                                       "Министерством культуры Российской Федерации «Модельным стандартом деятельности общедоступной "
                                       "библиотеки», законом Рязанской области «О библиотечном деле» и другими документами. "
                                       "Адрес: 390000, г. Рязань, ул. Ленина, д. 52 Контактный номер: + 7(4912)935-550"
                                       "Email: post@rounb.ru", reply_markup=url_int_button_6)
            if code == 7:
                await bot.send_message(callback_query.from_user.id,
                                       "D-Link " "Компания D-Link была основана на Тайване в 1986 г. и является ведущим мировым "
                                       "производителем сетевого оборудования корпоративного уровня и профессионального "
                                       "телекоммуникационного оборудования на основе технологий Metro Ethernet, PON, xDSL, Wi-Fi. "
                                       "Также D-Link занимает лидирующие позиции в производстве сетевого оборудования потребительского "
                                       "класса и устройств для «умного дома». " "В 1999 г. было открыто Представительство компании "
                                       "D-Link International в России, СНГ и странах Балтии. В настоящее время, помимо более чем 20 "
                                       "региональных подразделений в Российской Федерации, компания представлена офисами и центрами "
                                       "разработки в Беларуси, Казахстане, Армении, Украине, Молдове, Литве, Латвии и Эстонии."
                                       "В настоящее время российское подразделение R&D компании насчитывает более 100 человек, "
                                       "обладающих уникальными компетенциями по созданию клиентских устройств доступа в Интернет, "
                                       "адаптированных под требования ведущих федеральных и региональных провайдеров. Активно "
                                       "расширяющийся производственно-логистический комплекс компании способен в кратчайшие сроки "
                                       "удовлетворить постоянно возрастающее количество заказов клиентов."
                                       "Адрес: 390043, Рязань, пр.Шабулина, 16 Контактный номер: +7(4912)575-305 "
                                       "E-mail: ryazan@dlink.ru", reply_markup=url_int_button_7)
            if code == 8:
                await bot.send_message(callback_query.from_user.id, "Агентство интернет-маркетинга «Лидмашина»"
                                                                    "Помогаем малому и крупному бизнесу заработать в интернете. Беремся за B2B, B2C и B2G компании. "
                                                                    "Быстро и эффектно решаем маленькие задачи: настраиваем рекламу, собираем сайт на конструкторе, "
                                                                    "находим ошибки в рекламе, соцсетях,  SEO и на сайте. Выстраиваем системную работу для крупного "
                                                                    "бизнеса. Анализируем текущее положение дел, придумываем новые решения и дорабатываем старые. "
                                                                    "Можем создать сайт, запустить блог, заставить соцсети продавать или полностью забрать на себя "
                                                                    "интернет-маркетинг."
                                                                    "Адрес: 390000, г. Рязань, ул. Право-Лыбедская, д. 40 Контактный номер: +7(800)700-04-51, "
                                                                    "E-mail: moreleads@leadmachine.ru",
                                       reply_markup=url_int_button_8)

    if msg.text == 'Карьерные карты':
        button_1 = InlineKeyboardButton(text="Мобильная разработка", callback_data="btn1")
        button_2 = InlineKeyboardButton(text="Backend-разработка", callback_data="btn2")
        button_3 = InlineKeyboardButton(text="Data Science", callback_data="btn3")
        button_4 = InlineKeyboardButton(text="Frontend-разработка", callback_data="btn4")
        button_5 = InlineKeyboardButton(text="IT-архитектура", callback_data="btn5")
        button_6 = InlineKeyboardButton(text="IT-консалтинг", callback_data="btn6")
        button_7 = InlineKeyboardButton(text="QA тестирование", callback_data="btn7")
        button_8 = InlineKeyboardButton(text="Дизайн интерфейсов", callback_data="btn8")
        button_9 = InlineKeyboardButton(text="Бизнес-аналитика", callback_data="btn9")
        button_10 = InlineKeyboardButton(text="Геймдизайн", callback_data="btn!")
        button_11 = InlineKeyboardButton(text="Digital-маркетинг", callback_data="btn&")
        button_12 = InlineKeyboardButton(text="AR/VR-разработка", callback_data="btn^")
        button_13 = InlineKeyboardButton(text="Кибербезопасность", callback_data="btn_")
        button_14 = InlineKeyboardButton(text="Product менеджмент", callback_data="btn-")
        button_15 = InlineKeyboardButton(text="Развитие инноваций", callback_data="btn+")
        button_16 = InlineKeyboardButton(text="Системное администрирование", callback_data="btn~")
        button_17 = InlineKeyboardButton(text="Project менеджмент", callback_data="btn№")
        keyboard = InlineKeyboardMarkup().add(button_1).insert(button_2).add(button_3).insert(button_4).add(
            button_5).insert(button_6).add(button_7).insert(button_8).add(button_9).insert(button_10).add(
            button_11).insert(button_12).add(button_13).insert(button_14).add(button_15).insert(button_16).add(
            button_17)
        await msg.answer("Карьерные карты", reply_markup=keyboard)

        @dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn'))
        async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
            code = callback_query.data[-1]
            if code.isdigit():
                code = int(code)
            if code == 1:
                await bot.send_message(callback_query.from_user.id, '<strong>Мобильная разработка</strong>,'
                                                                    '\nМобильный разработчик — это специалист, который создает приложения для мобильных устройств. '
                                                                    '\nК таким устройствам относятся смартфоны, планшеты, умные часы, фитнес-трекеры, электронный книги, навигаторы и многие другие.'
                                                                    '\nБольшинство устройств работает под управлением операционных систем Android или iOS.'
                                                                    '\nГде можно получить навыки:'
                                                                    "\nhttps://www.rsu.edu.ru/wp-content/uploads/2019/11/%D0%A0%D0%B5%D0%BA%D0%BB%D0%B0%D0%BC%D0%B0_%D0%9C%D0%9E%D0%B8%D0%90%D0%98%D0%A1_2020.pdf"
                                                                    "\nhttp://rsreu.ru/faculties/fvt/kafedri/evm/menu-502/010500-matematicheskoe-obespechenie-i-administrirovanie-informatsionnykh-sistem"
                                                                    "\nhttp://rsreu.ru/faculties/fvt/kafedri/vpm/menu-504/230105-programmnoe-obespechenie-vychislitelnoj-tekhniki-i-avtomatizirovannykh-sistem"
                                                                    "\nhttp://rsreu.ru/faculties/fvt/kafedri/saprvs/menu-503/11-03-01-informatika-i-vychislitelnaya-tekhnika-bakalavriat",
                                       parse_mode="HTML")
                but1 = InlineKeyboardButton(text="Мл.Мобильный разработчик", callback_data="m*")
                but2 = InlineKeyboardButton(text="Мобильный разработчик", callback_data="m;")
                but3 = InlineKeyboardButton(text="Руководитель мобильной разработки", callback_data="m:")
                but4 = InlineKeyboardButton(text="ИТ-директор ", callback_data="m{")
                key = InlineKeyboardMarkup().add(but1).insert(but2).add(but3).insert(but4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('m'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "З/П — 30 000 - 60 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 2 года"
                                                                            "\nЭто специалист, обладающий теоретическими знаниями разработки. "
                                                                            "Часто – понимает основы алгоритмизации и основные структуры данных, "
                                                                            "возможности выбранного языка программирования и 1-2 фреймворков. "
                                                                            "Работает под строгим присмотром старших коллег, "
                                                                            "так как код младшего-разработчика нуждается в постоянной проверке.")
                    elif code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 60 000 - 150 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 2 / 4 года"
                                                                            "\nОпытный разработчик уже не требует сильного контроля со стороны старших и способен сам определять направление и метод реализации задач, "
                                                                            "которые ему ставит начальник. Он понимает процессы в команде, архитектуру продукта, продуктовый контекст и почему все так, "
                                                                            "а не иначе. Успешно решает задачи средней сложности длиной в неделю и более.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 150 000 – 250 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 5 лет"
                                                                            "\nРуководитель (TeamLead) знает несколько языков программирования, "
                                                                            "может с нуля реализовать архитектуру проекта, выбрать стек технологий. "
                                                                            "При решении поставленных задач видит общую картину, не привязывается к каким-то конкретным технологиям, "
                                                                            "умеет видеть наперед плюсы и минусы выбранных решений.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 250 000 – 400 000 ₽/мес"
                                                                            "\nCIO (Chief Information Officer), или ИТ-директор — это топ-менеджер,  "
                                                                            "который отвечает за информационные технологии (ИТ), "
                                                                            "особенно в ИТ-компаниях или компаниях, деятельность которых преимущественно базируется на ИТ-инфраструктуре."
                                                                            "Роль CIO в компании состоит в разработке информационной стратегии по управлению бизнесом на основе передовых цифровых технологий, "
                                                                            "а также в обеспечении ее ИТ-составляющих. Также CIO руководит сотрудниками ИТ-департамента, поддерживает рабочие связи с другими службами компании "
                                                                            "(единым проектным офисом, отделом бизнес-аналитики, подразделением информационной безопасности) и руководством."
                                                                            "CIO собирает сведения о выборе технологий, партнеров и оборудовании и предоставляет их генеральному директору (CEO) с обоснованием своих решений по выгодам и стоимости того или иного варианта "
                                                                            "(например, использования аутсорсинга вместо труда собственных сотрудников).")

                await bot.send_message(callback_query.from_user.id,
                                       '\nУ рекрутинговой компании есть сайт, на котором удобно искать работу с компьютера. '
                                       '\nНо пользователям также хотелось бы просматривать и откликаться на вакансии с телефона.'
                                       '\n Product-manager , изучив спрос пользователей, составляют задание на разработку мобильного приложения, а мобильные разработчики реализуют его технически.'
                                       'Подробнее о разработке и начальных требования : https://digitalway62.ru/karernye-karty/android-razrabotka/')

            if code == 2:
                await bot.send_message(callback_query.from_user.id,
                                       '\nBackend-разработка — это создание внутренней и вычислительной логики web-приложений, web-сайтов или других программных продуктов и информационных систем.'
                                       '\nПроще говоря, backend-разработчики имеют дело со всем, что не видит и напрямую не трогает обычный пользователь.'
                                       '\nК этому относится обеспечение корректной работы всех функций сайта, работа с базами данных посредством систем управления, разработка архитектуры, обеспечение интеграция со сторонними ресурсами.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/back-end-razrabotka/ '
                                       '\nГде можно получить навыки:'
                                       '\nВысшее образование:'
                                       "\nhttp://rsreu.ru/faculties/fvt/kafedri/vpm/menu-504/230105-programmnoe-obespechenie-vychislitelnoj-tekhniki-i-avtomatizirovannykh-sistem"
                                       "\nhttps://www.rsu.edu.ru/wp-content/uploads/2019/11/%D0%A0%D0%B5%D0%BA%D0%BB%D0%B0%D0%BC%D0%B0_%D0%9C%D0%9E%D0%B8%D0%90%D0%98%D0%A1_2020.pdf"
                                       '\nСреднее профессиональное образование:'
                                       '\nhttps://новый.ркэ.рф/assets/%D0%9F%D0%9A/spec/%D0%98%D0%A1%20%D0%B8%20%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5.pdf')
                buta1 = InlineKeyboardButton(text="Мл.Backend-рязработчик", callback_data="n*")
                buta2 = InlineKeyboardButton(text="Backend-рязработчик", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Руководитель backend-разработки", callback_data="n:")
                buta4 = InlineKeyboardButton(text="ИТ-директор ", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "З/П — 30 000 - 60 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 2 года"
                                                                            "\nЭто специалист, обладающий теоретическими знаниями разработки. "
                                                                            "Часто – понимает основы алгоритмизации и основные структуры данных, "
                                                                            "возможности выбранного языка программирования и 1-2 фреймворков. "
                                                                            "Работает под строгим присмотром старших коллег, "
                                                                            "так как код младшего-разработчика нуждается в постоянной проверке.")
                    elif code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 60 000 - 150 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 2 / 4 года"
                                                                            "\nОпытный разработчик уже не требует сильного контроля со стороны старших и способен сам определять направление и метод реализации задач, "
                                                                            "которые ему ставит начальник. Он понимает процессы в команде, архитектуру продукта, продуктовый контекст и почему все так, "
                                                                            "а не иначе. Успешно решает задачи средней сложности длиной в неделю и более.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 150 000 – 250 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 5 лет"
                                                                            "\nРуководитель (TeamLead) знает несколько языков программирования, "
                                                                            "может с нуля реализовать архитектуру проекта, выбрать стек технологий. "
                                                                            "При решении поставленных задач видит общую картину, не привязывается к каким-то конкретным технологиям, "
                                                                            "умеет видеть наперед плюсы и минусы выбранных решений.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 250 000 – 400 000 ₽/мес"
                                                                            "\nCIO (Chief Information Officer), или ИТ-директор — это топ-менеджер,  "
                                                                            "который отвечает за информационные технологии (ИТ), "
                                                                            "особенно в ИТ-компаниях или компаниях, деятельность которых преимущественно базируется на ИТ-инфраструктуре."
                                                                            "Роль CIO в компании состоит в разработке информационной стратегии по управлению бизнесом на основе передовых цифровых технологий, "
                                                                            "а также в обеспечении ее ИТ-составляющих. Также CIO руководит сотрудниками ИТ-департамента, поддерживает рабочие связи с другими службами компании "
                                                                            "(единым проектным офисом, отделом бизнес-аналитики, подразделением информационной безопасности) и руководством."
                                                                            "CIO собирает сведения о выборе технологий, партнеров и оборудовании и предоставляет их генеральному директору (CEO) с обоснованием своих решений по выгодам и стоимости того или иного варианта "
                                                                            "(например, использования аутсорсинга вместо труда собственных сотрудников).")

            if code == 3:
                await bot.send_message(callback_query.from_user.id, 'Дословно data science — наука о данных. '
                                                                    '\nОна объединяет в себе методы по сбору, обработке и анализу больших объемов данных (Big Data) с целью выделить из общего массива данных полезную для заказчика информацию.'
                                                                    '\nBig Data называют массивы информации со сложной, неоднородной структурой, как правило характеризующие состояние определенных объектов.'
                                                                    '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/data-science/'
                                                                    '\nГде можно получить навыки:'
                                                                    '\nВысшее образование:'
                                                                    "\nrsreu.ru/faculties/fvt/kafedri/saprvs/menu-503"
                                                                    "\nhttp://www.rsreu.ru/faculties/faitu/kafedri/aitu/menu-458/napravlenie-01-03-02-prikladnaya-matematika-i-informatika"
                                                                    '\nСреднее профессиональное образование:'
                                                                    '\nhttps://rgtc.ru/abiturientam/otdeleniya/otdelenie-informaczionnyix-texnologij/09.02.04-informaczionnyie-sistemyi.html')
                butb1 = InlineKeyboardButton(text="Младший продуктовый аналитик", callback_data="l*")
                butb2 = InlineKeyboardButton(text="Data Scientist ", callback_data="l;")
                butb3 = InlineKeyboardButton(text="Руководитель Data Science ", callback_data="l:")
                butb4 = InlineKeyboardButton(text="Директор по данным", callback_data="l{")
                keyb = InlineKeyboardMarkup().add(butb1).insert(butb2).add(butb3).insert(butb4)
                await msg.answer("Карьерный рост", reply_markup=keyb)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('l'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code2 = callback_query1.data[-1]
                    if code2.isdigit():
                        code2 = int(code2)
                    if code2 == "*":
                        await bot.send_message(callback_query.from_user.id, "З/П — 60 000 - 80 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 3 года"
                                                                            "В отличие от большинства профессий в data science нет как таковых начальных должностей. "
                                                                            "Чтобы занять эту позицию у человека в арсенале уже должен быть опыт работы в разработке или аналитике. "
                                                                            "Младший продуктовый аналитик — хороший вариант для старта. "
                                                                            "Он как раз решает задачи, связанные со сбором данных, и использует языки программирования R и Python.")
                    elif code2 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 180 000 - 250 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 5 лет"
                                                                            "\nData Scientist занимается сбором и анализом больших данных . Основная задача Data Scientist — проводить анализ не ради анализа, \n"
                                                                            "а чтобы вычленять из массивов данных информацию, которая может качественно улучшить работу заказчика.\n")
                    elif code2 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 250 000 – 500 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 4 / 6 лет"
                                                                            "\nЧеловек, стоящий во главе data science, в большой компании может управлять несколькими Data Scientist и Machine Learning инженерами. На этом уровне карьеры, \n"
                                                                            "как и у TeamLead в разработке, управленческие способности и стратегическое видение задачи играют большую роль,\n"
                                                                            "нежели hard skills. Важно уметь видеть картину целиком и предотвращать ошибки на старте проекта.\n")
                    elif code2 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 400 000 – 800 000 ₽/мес"
                                                                            "\nОсновное предназначение этой позиции – превращение данных в деньги путем разработки и внедрения инновационных идей на основе анализа накопленной информации. \n"
                                                                            "Основными задачами CDO (директора по данным) можно назвать:\n"
                                                                            "разработка и реализация концепции развития корпоративных данных;\n"
                                                                            "создание и поддержка единой архитектуры данных; обеспечение качества данных;\n"
                                                                            "участие в разработке и реализации корпоративных стратегий  и формировании требований к новым программным приложениям и хранилищам данных; подготовка и координация работы \n"
                                                                            "Data Stewards (специалистов, которые определяют требования и решают инциденты с качеством данных в рамках своего бизнес-подразделения); \n"
                                                                            "управление работой аналитиков, инженеров, исследователей, администраторов данных; эффективная организация процессов управления данными.\n")
            if code == 4:
                await bot.send_message(callback_query.from_user.id,
                                       'Frontend-разработка — это создание внешнего интерфейса web-сайта или другого программного продукта.'
                                       '\nИменно frontend-разработчик отвечает за логичную работу всех компонентов сайта, включая графические изображения, навигацию и кнопки, контент и внутренние ссылки.'
                                       '\nОни воплощают работы дизайнеров в жизнь, определяют как взаимодействует backend и дизайн с пользователем, то есть отвечают за клиентскую сторону пользовательского интерфейса.'
                                       '\nFrontend-разработчики взаимодействуют с органами зрения, слуха, а иногда и осязания обычных людей.'
                                       '\nПодробнее о примерных задачах и начальных требованиях:https://digitalway62.ru/karernye-karty/front-end-razrabotka/'
                                       '\nГде можно получить навыки для данной профессии:'
                                       '\nВысшее образование:'
                                       '\nrsreu.ru/faculties/fvt/kafedri/saprvs/menu-503/11-03-01-informatika-i-vychislitelnaya-tekhnika-bakalavriat'
                                       '\nСреднее профессиональное образование:'
                                       '\nhttps://новый.ркэ.рф/assets/%D0%9F%D0%9A/spec/%D0%98%D0%A1%20%D0%B8%20%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5.pdf')
                buta1 = InlineKeyboardButton(text="Мл.Frontend-рязработчик", callback_data="n*")
                buta2 = InlineKeyboardButton(text="frontend-рязработчик", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Руководитель frontend-разработки", callback_data="n:")
                buta4 = InlineKeyboardButton(text="ИТ-директор ", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "З/П — 30 000 - 60 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 2 года"
                                                                            "\nЭто специалист, обладающий теоретическими знаниями разработки. "
                                                                            "Часто – понимает основы алгоритмизации и основные структуры данных, "
                                                                            "возможности выбранного языка программирования и 1-2 фреймворков. "
                                                                            "Работает под строгим присмотром старших коллег, "
                                                                            "так как код младшего-разработчика нуждается в постоянной проверке.")
                    elif code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 60 000 - 150 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 2 / 4 года"
                                                                            "\nОпытный разработчик уже не требует сильного контроля со стороны старших и способен сам определять направление и метод реализации задач, "
                                                                            "которые ему ставит начальник. Он понимает процессы в команде, архитектуру продукта, продуктовый контекст и почему все так, "
                                                                            "а не иначе. Успешно решает задачи средней сложности длиной в неделю и более.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 150 000 – 250 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 5 лет"
                                                                            "\nРуководитель (TeamLead) знает несколько языков программирования, "
                                                                            "может с нуля реализовать архитектуру проекта, выбрать стек технологий. "
                                                                            "При решении поставленных задач видит общую картину, не привязывается к каким-то конкретным технологиям, "
                                                                            "умеет видеть наперед плюсы и минусы выбранных решений.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 250 000 – 400 000 ₽/мес"
                                                                            "\nCIO (Chief Information Officer), или ИТ-директор — это топ-менеджер,  "
                                                                            "который отвечает за информационные технологии (ИТ), "
                                                                            "особенно в ИТ-компаниях или компаниях, деятельность которых преимущественно базируется на ИТ-инфраструктуре."
                                                                            "Роль CIO в компании состоит в разработке информационной стратегии по управлению бизнесом на основе передовых цифровых технологий, "
                                                                            "а также в обеспечении ее ИТ-составляющих. Также CIO руководит сотрудниками ИТ-департамента, поддерживает рабочие связи с другими службами компании "
                                                                            "(единым проектным офисом, отделом бизнес-аналитики, подразделением информационной безопасности) и руководством."
                                                                            "CIO собирает сведения о выборе технологий, партнеров и оборудовании и предоставляет их генеральному директору (CEO) с обоснованием своих решений по выгодам и стоимости того или иного варианта "
                                                                            "(например, использования аутсорсинга вместо труда собственных сотрудников).")
            if code == 5:
                await bot.send_message(callback_query.from_user.id,
                                       'IT-архитектор — это специалист, который решает, как в конечном итоге будет выглядеть информационная система компании.'
                                       '\nОн помогает компаниям применять информационные технологии, чтобы автоматизировать и упрощать бизнес-процессы, экономить деньги и улучшать пользовательский опыт.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/it-arhitektura/'
                                       '\nГде можно получить навыки для данной профессии:'
                                       '\nВысшее образование:'
                                       '\nhttp://rsreu.ru/faculties/fvt/kafedri/evm/menu-502/230100-informatika-i-vychislitelnaya-tekhnika'
                                       '\nСреднее профессиональное образование:'
                                       '\nhttps://новый.ркэ.рф/assets/%D0%9F%D0%9A/spec/%D0%98%D0%A1%20%D0%B8%20%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5.pdf')
                buta1 = InlineKeyboardButton(text="Мл.Системный аналитик ", callback_data="n*")
                buta2 = InlineKeyboardButton(text="IT-архитектор", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Руководитель IT-проектов", callback_data="n:")
                buta4 = InlineKeyboardButton(text="Технический директор", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "З/П — 40 000 - 60 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 3 года"
                                                                            "\nДля прихода в профессию IT-архитектора необходим профессиональный опыт в разработке, системном администрировании или в системной аналитике, так как системный аналитик — это связующее звено бизнеса и разработчиков. \n"
                                                                            "Он отвечает за процесс взаимодействия между заказчиком (внутренним или внешним) и командой разработки.")
                    elif code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 100 000 - 150 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 5 лет"
                                                                            "\nIT-архитектор — хорошо знает весь процесс технической реализации проекта и, наряду с этим, обладает компетенциями менеджера проекта. Он должен уметь убеждать начальство/клиента в необходимости преобразований IT-инфраструктуры. \n"
                                                                            "People management и умение продавать свои идеи — основополагающие компетенции для человека на этой позиции. Важно понимать, \n"
                                                                            "что не в каждой компании есть данная позиция. В основном она встречается в крупных корпорациях с разветвленной IT-системой.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 180 000 – 300 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 6 лет"
                                                                            "\nЛогичная ступень роста для IT-архитектора — это руководитель IT-проекта или группы проектов. За счет глубокого понимания ПО и бизнес-процессов компании, руководитель может отвечать одновременно за такие разные проекты, \n"
                                                                            "как автоматизация найма сотрудников и автоматизация отчетности и документооборота.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 300 000 – 1 000 000 ₽/мес"
                                                                            "\nТехнический директор (Chief Technical Officer, CTO) подбирает инновационные методы, которые дают компании возможности достижения стратегических целей, а также отвечает за технологии, исследования и разработки, контролирует развитие технологий, предназначенных для коммерциализации. \n"
                                                                            "В круг обязанностей СТО могут входить определение общих стратегий технического развития, принятие глобальных технических решений, выбор и оценка технологий, определение длительности и трудоемкости проектов, написание и обзоры кодов, управление техническими рисками на проектах;")
            if code == 6:
                await bot.send_message(callback_query.from_user.id,
                                       'IT-консалтинг — один из множества видов консалтинга на рынке.'
                                       '\nЕго задача — консультирование бизнеса по вопросам IT-сферы и внедрение таких IT-решений, которые помогают компании зарабатывать больше и работать эффективнее.'
                                       '\nИными словами, IT-консалтинг помогает компаниям выбрать наилучший вариант использования и внедрения IT-систем и продуктов.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/it-konsalting/'
                                       '\nГде можно получить навыки для данной профессии:'
                                       '\nВысшее образование:'
                                       '\nhttp://rsreu.ru/faculties/fvt/kafedri/kt/uchebnaya-rabota/napravlenie-09-03-01-informatika-i-vychislitelnaya-tekhnika-stepen-bakalavr-po-obrazovatelnoj-programme-sistemnyj-analiz-i-inzhinirika-informatsionnykh-protsessov'
                                       '\nСреднее профессиональное образование:'
                                       '\nhttps://rgtc.ru/abiturientam/otdeleniya/otdelenie-informaczionnyix-texnologij/09.02.04-informaczionnyie-sistemyi.html')
                buta1 = InlineKeyboardButton(text="Мл.Системный аналитик ", callback_data="n*")
                buta2 = InlineKeyboardButton(text="IT-консультант ", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Менеджер проекта ", callback_data="n:")
                buta4 = InlineKeyboardButton(text="Принципал / Партнер ", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "З/П — 40 000 - 70 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 2 года"
                                                                            "Начинать путь в IT-консалтинг можно с должности младшего системного аналитика. Он умеет говорить на одном языке и с разработчиками, которые отвечают за создание продукта, и с бизнесом, который ставит задачи. \n"
                                                                            "Занимается написанием технического задания команде разработки и документированием уже реализованного функционала.")
                    elif code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 120 000 - 200 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 2 / 5 года"
                                                                            "\nIT-консультант хорошо знает весь процесс технической реализации проекта и, наряду с этим, обладает компетенциями менеджера: взаимодействует с заказчиками и внутренней ИТ-службой для определения лучшего варианта решения проблемы. \n"
                                                                            "Знает гибкие методологии управления проектами (Kanban, Scrum) и умеет их применять.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 200 000 – 400 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 6 лет"
                                                                            "\nМенеджер занимается проектами по цифровой трансформации и внедрению современных технологий в бизнес, выполняет стратегически важные IT проекты для компании-заказчика. Контролирует весь цикл выполнения проекта, \n"
                                                                            "обладает сильной технической экспертизой, умеет ставить задачи команде разработчиков и тестировщиков.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 500 000 – 1 500 000 ₽/мес"
                                                                            "\nВ любом виде консалтинга, включая IT консалтинг, принципалы и партнеры являются главами практик и работают с клиентами из отрасли на которой специализируются. Например глава практики по внедрению IT решений в банки, \n"
                                                                            "тяжелую промышленность, FMCG и так далее. Основная задача принципалов и партнеров — приводить новых клиентов и удерживать старых, поэтому их доход во многом складывается не только из зарплаты, но и из бонусов с проектов.")
            if code == 7:
                await bot.send_message(callback_query.from_user.id,
                                       '\nДословно с английского QA — это Quality Assurance, то есть обеспечение качества продукта на всех этапах разработки или по-русски — тестирование.'
                                       '\nОсновная задача тестировщика — найти в программе, приложении, игре или другом продукте все возможные ошибки и проблемы до того, как продукт выкачен на пользователя.'
                                       '\nТо есть до того, как им стали пользоваться мы с вами.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/qa-testirovanie/'
                                       '\nГде можно получить навыки для данной профессии:'
                                       '\nВысшее образование:'
                                       '\nhttp://rsreu.ru/faculties/fvt/kafedri/vpm/menu-504/230105-programmnoe-obespechenie-vychislitelnoj-tekhniki-i-avtomatizirovannykh-sistem'
                                       '\nСреднее профессиональное образование:'
                                       '\nhttps://новый.ркэ.рф/assets/%D0%9F%D0%9A/spec/%D0%98%D0%A1%20%D0%B8%20%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5.pdf')
                buta1 = InlineKeyboardButton(text="Младший-QA инженер / Тестировщик ", callback_data="n*")
                buta2 = InlineKeyboardButton(text="QA-инженер / Тестировщик ", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Руководитель QA", callback_data="n:")
                buta4 = InlineKeyboardButton(text="ИТ-директор", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "З/П — 30 000 - 60 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 2 года"
                                                                            "\nВ обязанности младших тестировщиков входит ручное тестирование по готовым сценариям и написание базовых тест-кейсов. \n"
                                                                            "Всю работу контролируют более опытные специалисты. Джун выполняет простую ручную работу и не связан с процессами улучшения качества продукта в целом. Его основная задача — выявлять ошибки.")
                    elif code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 60 000 - 150 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 3 года"
                                                                            "\nОпытный тестировщик занимается повышением качества продукта на всех этапах разработки. То есть разрабатывает и устанавливает стандарты качества, выбирает инструменты тестирования, обдумывает, как предотвратить ошибки. \n"
                                                                            "Формулирует требования к разрабатываемым системам и компонентам. Тестировщики, умеющие делать автоматические запросы, ценятся на рынке больше.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 150 000 – 250 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 5 лет"
                                                                            "\nРуководитель (тимлид) принимает решения по внутреннему устройству, требованиям и внешним интерфейсам ПО. Выполняет сложные задачи по тестированию. Он же координирует стратегию тестирования в небольшой команде, \n"
                                                                            "руководит тестировщиками, планирует их работу. Оценивает объём, сроки выполнения и бюджет проекта.")

                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 250 000 – 400 000 ₽/мес"
                                                                            "\nCIO (Chief Information Officer), или ИТ-директор — это топ-менеджер,  "
                                                                            "который отвечает за информационные технологии (ИТ), "
                                                                            "особенно в ИТ-компаниях или компаниях, деятельность которых преимущественно базируется на ИТ-инфраструктуре."
                                                                            "Роль CIO в компании состоит в разработке информационной стратегии по управлению бизнесом на основе передовых цифровых технологий, "
                                                                            "а также в обеспечении ее ИТ-составляющих. Также CIO руководит сотрудниками ИТ-департамента, поддерживает рабочие связи с другими службами компании "
                                                                            "(единым проектным офисом, отделом бизнес-аналитики, подразделением информационной безопасности) и руководством."
                                                                            "CIO собирает сведения о выборе технологий, партнеров и оборудовании и предоставляет их генеральному директору (CEO) с обоснованием своих решений по выгодам и стоимости того или иного варианта "
                                                                            "(например, использования аутсорсинга вместо труда собственных сотрудников).")
            if code == 8:
                await bot.send_message(callback_query.from_user.id,
                                       'UX-дизайн — это проектирование интерфейса на основе исследования пользовательского опыта и поведения.'
                                       '\nЗадача UX-дизайнера — сделать так, чтобы нам было удобно пользоваться приложением или сайтом.'
                                       '\nПо факту, это инженер-конструктор и бизнес-аналитик в одном флаконе, который продумывает процессы и логику продукта.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/ui-dizajn/'
                                       '\nГде можно получить навыки для данной профессии:'
                                       '\nВысшее образование:'
                                       '\nhttps://www.rsu.edu.ru/wp-content/uploads/2019/11/Реклама_МОиАИС_2020.pdf'
                                       '\nСреднее профессиональное образование:'
                                       '\nhttps://новый.ркэ.рф/assets/%D0%9F%D0%9A/spec/%D0%98%D0%A1%20%D0%B8%20%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5.pdf')
                buta1 = InlineKeyboardButton(text="Младший UX/UI-дизайнер", callback_data="n*")
                buta2 = InlineKeyboardButton(text="UX/UI-дизайнер ", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Руководитель группы дизайнеров ", callback_data="n:")
                buta4 = InlineKeyboardButton(text="Арт-директор", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "З/П — 40 000 - 60 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 2 года"
                                                                            "\nМладший дизайнер выполняет задачи, поставленные коллегами старше. \n"
                                                                            "Он понимает основы пользовательского опыта и знаком с 1-2 программами типа Figma или Axure. Однако эти знания обычно не систематизированы. Поэтому джун работает под строгим присмотром старших коллег и его работа нуждается в постоянном ревью.")
                    elif code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 80 000 - 180 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 2 / 3 года"
                                                                            "\nПолноценный дизайнер в отличие от джуна уже не требует сильного контроля со стороны старших и способен сам определять направление и метод реализации задачи. Способен сделать блок работы так, что за ним не придется переделывать. \n"
                                                                            "Делает не просто задачи, поставленные сверху, но предлагает варианты по улучшению работы.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 180 000 – 250 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 6 лет"
                                                                            "\nРуководитель группы (тимлид) управляет работой менее опытных дизайнеров. Он видит общую картину и способен предугадать проблемы, которые возникнут на этапе реализации. При этом самостоятельно UX и UI-дизайн он рисует меньше, \n"
                                                                            "зато может беглым взглядом выявить ошибки и упущения новобранцев. Управляет проектом, нанимает и обучает новичков.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 250 000 – 600 000 ₽/мес"
                                                                            "Арт-директор — это стратег и идейный вдохновитель. Он задает концепцию, стиль, жанр, эстетику визуальных образов и макетов. Является конечным контролёром качества и помогает команде выйти из тупика при реализации проекта. Обладает огромной насмотренностью на лучшие работы, практики и тренды на рынке.")
            if code == 9:
                await bot.send_message(callback_query.from_user.id,
                                       'Бизнес-аналитика — это вид аналитики, основная задача которого — выявлять проблемы бизнеса (узкие горлышки в процессах,операциях, структуре) и предлагать их решение.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/biznes-analitika/'
                                       '\nГде можно получить навыки для данной профессии:'
                                       '\nВысшее образование:'
                                       '\nhttp://rsreu.ru/faculties/fvt/kafedri/evm/menu-502/010500-matematicheskoe-obespechenie-i-administrirovanie-informatsionnykh-sistem'
                                       'http://www.rsreu.ru/faculties/fvt/kafedri/evm/menu-502/010500-matematicheskoe-obespechenie-i-administrirovanie-informatsionnykh-sistem-2'
                                       '\nhttp://www.rsreu.ru/faculties/faitu/kafedri/aitu/menu-458/napravlenie-01-03-02-prikladnaya-matematika-i-informatika')
                buta1 = InlineKeyboardButton(text="Бизнес-аналитик", callback_data="n*")
                buta2 = InlineKeyboardButton(text="Старший бизнес-аналитик ", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Руководитель отдела бизнес-анализа  ", callback_data="n:")
                buta4 = InlineKeyboardButton(text="Директор по аналитике", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "З/П — 50 000 - 90 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 2 года"
                                                                            "Бизнес-аналитик работает над сбором сырых данных, много работает с Excel, готовит презентации для руководства. \n"
                                                                            "Помогает старшим коллегам с формированием предварительных выводов по задаче и иногда участвует в интервьюировании внутренних сотрудников компании для полноценного анализа проблемы.")
                    if code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 90 000 - 180 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 2 / 3 года"
                                                                            "Старший БА следит за работой младших аналитиков, обладает опытом управления небольшой командой, часто несет ответственность за 1-2 проекта и выполняет роль проектного менеджера. \n"
                                                                            "Он же коммуницирует с коллегами из смежных подразделений — с отделом коммерции, маркетинга, финансов.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 200 000 – 400 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 2 / 3 лет"
                                                                            "Руководитель полностью выстраивает работу отдела и несет ответственность за все проекты перед топ-менеждментом. \n"
                                                                            "Часто отдел бизнес-анализа бывает прикреплен в бОльшей функции в компании. Например, к финансовому, коммерческому или блоку стратегии. В зависимости от структуры компании глава бизнес-анализа может подчиняться финансовому, коммерческому директору по стратегии или директору по аналитике.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 300 000 – 700 000 ₽/мес"
                                                                            "\nДиректор по аналитике определяет стратегические задачи и управляет всей командой аналитики (продуктовой, бизнес-аналитикой, маркетинговой). Его главная задача — сделать так, чтобы данные приносили бизнесу новые точки роста и дополнительную прибыль. Зарплата на уровне директора зависит от размера компании.")
            if code == '!':
                await bot.send_message(callback_query.from_user.id,
                                       'Геймдизайн — это не столько вид традиционного дизайна, сколько управление процессом создания игры: в чем будет заключаться сюжет игры, какой набор действий будет предлагаться игроку,'
                                       '\n как он будет взаимодействовать с игровым миром.'
                                       '\n Над игрой работает множество специалистов — программистов, художников, моделлеров. Геймдизайнер координирует их работу и связывает все части игры воедино.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/gejmdizajn/'
                                       '\nГде можно получить навыки для данной профессии:'
                                       '\nСреднее профессиональное образование:'
                                       '\nhttps://новый.ркэ.рф/assets/%D0%9F%D0%9A/spec/%D0%98%D0%A1%20%D0%B8%20%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5.pdf')

                buta1 = InlineKeyboardButton(text="Младший геймдизайнер ", callback_data="n*")
                buta2 = InlineKeyboardButton(text="Геймдизайнер ", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Руководитель группы геймдизайнеров", callback_data="n:")
                buta4 = InlineKeyboardButton(text="Креативный директор", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "З/П — 40 000 - 60 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 2 года"
                                                                            "\nУ геймдизайнеров, как и у разработчиков, уровни делятся на джун, миддл и синьор. Младшему дизайнеру дают какую-нибудь несложную область деятельности — как правило, \n"
                                                                            "роль UI-дизайнера на подхвате. Постоянно работает вместе со старшими коллегами и вторые проверяют, чтобы джун не сделал ерунды.")
                    if code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 80 000 - 180 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 2 / 3 года"
                                                                            "Как и джун, геймдизайнер работает в тесной связке со старшими коллегами, но понемногу определяется со своей специальностью. Учится выполнять свою часть работы без надзора синьоров, прокачивает технические навыки, \n"
                                                                            "но пока не управляет младшими дизайнерами и стажерами.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 180 000 – 250 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 6 лет"
                                                                            "\nРуководитель (или тимлид)— это старший дизайнер с лидерскими навыками, умением видеть проблемы наперед и обязанностью следить за работой отдела. Имеет полную информацию об игре, о запланированных фичах, \n"
                                                                            "о рабочей нагрузке джунов и миддлов. Мало делает руками, больше управляет подчиненными и ставит им задачи.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 250 000 – 600 000 ₽/мес"
                                                                            "\nСамая ответственная позиция в иерархии: от него исходит видение проекта и цели на ближайшую и дальнюю перспективы. При этом не чурается и самостоятельно писать документацию или возиться с балансом. \n"
                                                                            "Для геймдизайнера «стать креативным» означает иметь неограниченную возможность экспериментировать — и это высшее желание, к которому можно и нужно стремиться в данной профессии.")
            if code == '&':
                await bot.send_message(callback_query.from_user.id,
                                       'Digital-маркетинг — это комплекс мероприятий и инструментов, нацеленных на продвижение продукта или услуги в интернете.'
                                       '\nВ диджитал-маркетинг входят такие направления, как performance-маркетинг, e-mail маркетинг, работа с соцсетями (SMM), контент-менеджмент и веб-аналитика.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/didzhital-marketing/')
                buta1 = InlineKeyboardButton(text="Специалист по Digital-маркетингу", callback_data="n*")
                buta2 = InlineKeyboardButton(text="Менеджер по digital-маркетингу", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Руководитель отдела digital-маркетинга", callback_data="n:")
                buta4 = InlineKeyboardButton(text="Директор по маркетингу", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "З/П — 40 000 - 60 000 ₽/мес"
                                                                            "\nРаботает на-позиции 1 / 2 года"
                                                                            "\nСпециалист много работает руками и выполняет поручения старших коллег. Например, он помогает настраивать, вести и оптимизировать кампании в КМС (контекстно-медийная сеть Гугла) и РСЯ (рекламная сеть Яндекса). \n"
                                                                            "Он же анализирует входящий трафик и поведение пользователей на сайте.")
                    if code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 80 000 - 180 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 2 / 5 лет"
                                                                            "\nМенеджер обычно управляет небольшой командой digital-специалистов из 1-3 человек, взаимодействует с подрядчиками (digital и рекламными агентствами) и заключает партнерства — например, коллаборации с другими компаниями. \n"
                                                                            "В некоторых компаниях структура плоская и существенной разницы между функционалом менеджера и специалиста нет")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 200 000 – 400 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 6 лет"
                                                                            "\nРуководитель задает стратегию развития и транслирует её менеджерам и специалистам. Он отвечает за итоговый коммерческий результат всех digital-кампаний и проектов. Например, если digital-интеграция с Youtube-блоггером провалилась и не принесла компании новых клиентов или лидов, \n"
                                                                            "то отвечать за неудачу будет именно руководитель отдела.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 300 000 – 1 500 000 ₽/мес"
                                                                            "\nДиректору по маркетингу подчиняется не только отдел digital-маркетинга, но, например, направление PR и коммуникаций и оффлайн-маркетинг. Он отвечает за продвижение брендов или сервисов компании не только в онлайне, но и в оффлайне. \n"
                                                                            "То есть любая маркетинговая активность компании — от рекламных баннеров в метро до видеороликов с участием знаменитостей — это его зона ответственности.")
            if code == '^':
                await bot.send_message(callback_query.from_user.id,
                                       'AR/VR-разработчик — это программист,  который разрабатывает приложения виртуальной и дополненной реальности.'
                                       '\nVR предполагает полное погружение в созданный мир.'
                                       '\nГарнитура в виде очков и шлема создаёт имитацию реальности, которая передает ощущения на органы чувств.'
                                       '\nДополненная реальность (AR) добавляет цифровых эффектов в реальный мир, как например, маски в Instagram.'
                                       '\nЭто человек, создающий целые миры и пространства, людей, животных или фэнтезийных существ.'
                                       '\nТакже AR/VR-разработчик участвует в создании очков, шлема, перчаток и костюма виртуальной реальности.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/dizajn-intererov/')
                buta1 = InlineKeyboardButton(text="Мл.AR/VR-разработчик ", callback_data="n*")
                buta2 = InlineKeyboardButton(text="AR/VR-разработчик ", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Руководитель AR/VR-разработки ", callback_data="n:")
                buta4 = InlineKeyboardButton(text="ИТ-директор  ", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "З/П — 40 000 - 60 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 2 года"
                                                                            "\nЭто специалист, обладающий теоретическими знаниями разработки. "
                                                                            "Часто – понимает основы алгоритмизации и основные структуры данных, "
                                                                            "возможности выбранного языка программирования и 1-2 фреймворков. "
                                                                            "Работает под строгим присмотром старших коллег, "
                                                                            "так как код младшего-разработчика нуждается в постоянной проверке.")
                    elif code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 60 000 - 140 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 2 / 3 года"
                                                                            "\nОпытный разработчик уже не требует сильного контроля со стороны старших и способен сам определять направление и метод реализации задач, "
                                                                            "которые ему ставит начальник. Он понимает процессы в команде, архитектуру продукта, продуктовый контекст и почему все так, "
                                                                            "а не иначе. Успешно решает задачи средней сложности длиной в неделю и более.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 150 000 – 250 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 4 года"
                                                                            "\nРуководитель управляет технической работой менее опытных дизайнеров и помогает им в работе с клиентами. Он видит общую картину и способен предугадать проблемы, которые возникнут на этапе реализации. \n"
                                                                            "Сам он редко технически выполняет проекты, зато может беглым взглядом выявлять ошибки и упущения новобранцев.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 250 000 – 600 000 ₽/мес"
                                                                            "\nCIO (Chief Information Officer), или ИТ-директор — это топ-менеджер,  "
                                                                            "который отвечает за информационные технологии (ИТ), "
                                                                            "особенно в ИТ-компаниях или компаниях, деятельность которых преимущественно базируется на ИТ-инфраструктуре."
                                                                            "Роль CIO в компании состоит в разработке информационной стратегии по управлению бизнесом на основе передовых цифровых технологий, "
                                                                            "а также в обеспечении ее ИТ-составляющих. Также CIO руководит сотрудниками ИТ-департамента, поддерживает рабочие связи с другими службами компании "
                                                                            "(единым проектным офисом, отделом бизнес-аналитики, подразделением информационной безопасности) и руководством."
                                                                            "CIO собирает сведения о выборе технологий, партнеров и оборудовании и предоставляет их генеральному директору (CEO) с обоснованием своих решений по выгодам и стоимости того или иного варианта "
                                                                            "(например, использования аутсорсинга вместо труда собственных сотрудников).")

            if code == '_':
                await bot.send_message(callback_query.from_user.id,
                                       'Кибер-безопасность — это раздел IT, который занимается анализом информационных рисков компании, разработкой и внедрением мероприятий по их предотвращению.'
                                       '\nЕго основная задача — сделать так, чтобы злоумышленники не украли данные компании и отдельных пользователей и воспользовались ими.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/kiber-bezopasnost/'
                                       '\nГде можно получить навыки для данной профессии:'
                                       '\nВысшее образование:'
                                       '\nhttp://rsreu.ru/faculties/fvt/kafedri/ib/menu-1237/090301-kompyuternaya-bezopasnost'
                                       '\nhttp://rsreu.ru/faculties/fvt/kafedri/ib/menu-1237/090303-informatsionnaya-bezopasnost-avtomatizirovannykh-sistem'
                                       '\nСреднее профессиональное образование:'
                                       '\nhttps://новый.ркэ.рф/assets/%D0%9F%D0%9A/spec/%D0%9E%D0%98%D0%91.pdf')
                buta1 = InlineKeyboardButton(text="Специалист по информационной безопасности", callback_data="n*")
                buta2 = InlineKeyboardButton(text="Менеджер по информационной безопасности", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Руководитель отдела информационной безопасности", callback_data="n:")
                buta4 = InlineKeyboardButton(text="ИТ-директор  ", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "З/П — 50 000 - 80 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 3 года"
                                                                            "\nВнутри отела IT безопасности есть еще куча подразделений, например, public key infrastructure, антифрод, реагирование на инциденты, криптография. \n"
                                                                            "Можно попасть в какое-то одно направление и сильно углубиться в него, а можно расти вширь и набираться знаний из разных направлений. Специалисты работают под строгим присмотром старших, тестируют уязвимости, учатся предотвращать ошибки и утечки.")
                    elif code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 90 000 - 200 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 5 лет"
                                                                            "\nМенеджер занимается поиском потенциальных уязвимостей систем (то есть думает о проблемах наперед), разрабатывает новые средства автоматизации контроля. Он же проводит консультации по IT безопасности с работниками компании и помогает им в решении возникших проблем. \n"
                                                                            "Зарплата менеджеров и специалистов напрямую зависит от отрасли. Чем выше риски для отрасли (например, для банков), тем выше зарплата кибер-безопасников.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 300 000 – 600 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 5 / 10 года"
                                                                            "\nРуководитель отдела — крайне ответственная позиция. За все провалы безопасности именно он отвечает головой перед пользователями и руководством. \n"
                                                                            "Одна из его главных компетенций — умение выстроить отношения со всеми подразделениями внутри компании для обеспечения IT безопасности всей системы. Иногда для человека на этой позиции ограничены выезды за границу.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 400 000 – 800 000 ₽/мес"
                                                                            "\nЗанимается внутренней инфраструктурой и информационной средой, необходимой для работы всей компании: телекоммуникационной инфраструктурой, серверами и центрами обработки данных."
                                                                            "В обязанности входит работа не только с подразделением разработки (то есть, с Техническим директором) но также с другими функциями (продажи, маркетинг, финансы, бухгалтерия, HR).")
            if code == '-':
                await bot.send_message(callback_query.from_user.id,
                                       "Product менеджмент — это полный цикл создания продукта от появления идеи до его продвижения на рынке."
                                       '\nЛюди, работающие в этой сфере, находятся на стыке нескольких профессиональных сфер — маркетинга, разработки и развития бизнеса.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/prodakt-menedzhment/'
                                       '\nГде можно получить навыки для данной профессии:'
                                       '\nВысшее образование:'
                                       '\nhttp://rsreu.ru/faculties/fvt/kafedri/vpm/menu-504/230105-programmnoe-obespechenie-vychislitelnoj-tekhniki-i-avtomatizirovannykh-sistem')

                buta1 = InlineKeyboardButton(text="Младший продуктовый аналитик", callback_data="n*")
                buta2 = InlineKeyboardButton(text="Product менеджер", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Директор по продукту", callback_data="n:")
                buta4 = InlineKeyboardButton(text="Генеральный директор IT сервиса/компании", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "60 000 – 80 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 3 года"
                                                                            "Для того чтобы круто управлять продуктом, нужно быть хорошо подкованным в нескольких профессиональных областях сразу, одна из которых — продуктовая аналитика. Product менеджеры часто вырастают из продуктовых аналитиков, потому что вторые говорят на языке цифр и метрик и выдвигают гипотезы на основе данных.")
                    elif code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 150 000 - 250 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 6 лет"
                                                                            "\nProduct менеджер полноценно управляет продуктом: изучает желания пользователей, проводит конкурентный анализ, строит экономику бизнеса. Затем он составляет план изменений в продукте, формирует концепцию и отслеживает этапы работы. \n"
                                                                            "В зависимости от структуры компании product менеджеров может быть не один, а несколько.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 300 000 – 600 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 4 / 7 лет"
                                                                            "\nЗадача хорошего директора по продукту — определять долгосрочную и жизнеспособную стратегию развития одного продукта или линейки продуктов. Такие люди не раз запускали проекты с нуля: они понимают, \n]"
                                                                            "как создавать новые продукты и как трансформировать существующие. Директор по продукту — это прямая ступень к позиции CEO в IT компании.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 500 000 – 2 000 000 ₽/мес"
                                                                            "СЕО — это руководитель высшего звена («всех начальников начальник»), который занимает лидирующие позиции в организации и несет ответственность за реализацию существующих планов и политик, \n"
                                                                            "обеспечение успешного управления бизнесом, определение будущей стратегии и рост рыночной стоимости компании.Главный исполнительный директор (СЕО) не только управляет внутренней средой компании (кадры, финансы, технологии и т.п.), но и активно взаимодействует с внешней средой (акционеры, инвесторы, органы государственной власти, проверяющие и контролирующие органы, поставщики, банки, страховые компании, аудиторы и т.п.).")
            if code == '+':
                await bot.send_message(callback_query.from_user.id,
                                       'Направление внутри компании, которое занимается разработкой и внедрением новых технологий в механизмы и бизнес-процессы корпорации.'
                                       '\nПринципы работы этого отдела схожи с работой бизнес- и системных аналитиков: нужно найти процесс, который плохо работает, проанализировать проблему и придумать решение.'
                                       '\nА потом это решение вместе с IT департаментом воплотить в жизнь. Поэтому многие менеджеры по инновациям вырастают из аналитиков.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/razvitie-innovaczij/'
                                       '\nГде можно получить навыки для данной профессии:'
                                       '\nВысшее образование:'
                                       '\nhttp://rsreu.ru/faculties/fvt/kafedri/evm/menu-502/010500-matematicheskoe-obespechenie-i-administrirovanie-informatsionnykh-sistem'
                                       '\nhttp://www.rsreu.ru/faculties/faitu/kafedri/aitu/menu-458/napravlenie-01-03-02-prikladnaya-matematika-i-informatika')
                buta1 = InlineKeyboardButton(text="Бизнес-аналитик ", callback_data="n*")
                buta2 = InlineKeyboardButton(text="Старший бизнес-аналитик", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Менеджер по инновациям ", callback_data="n:")
                buta4 = InlineKeyboardButton(text="Директор по внедрению инноваций", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "50 000 – 90 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 2 года"
                                                                            "\nБизнес-аналитик работает над собором сырых данных, много копается с Excel, \n"
                                                                            "готовит презентации для руководства. Помогает старшим коллегам с формированием предварительных выводов по задаче и иногда участвует в интервьюировании внутренних сотрудников компании для полноценного анализа проблемы.")
                    elif code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 90 000 - 180 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 4 года"
                                                                            "\nСтарший БА следит за работой младших аналитиков, обладает опытом управления небольшой командой, часто несет ответственность за отдельный проект. Если компания небольшая, то выполняет роль проектного менеджера. \т"
                                                                            "Он же коммуницирует с коллегами из смежных подразделений — с отделом коммерции, маркетинга, финансов.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 250 000 – 400 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 5 лет"
                                                                            "\nВ связи с увеличением спроса у компаний на автоматизацию и диджитализацию стали появляться запросы и на людей, которые этими изменениями и внедрениями управляют. Менеджер по инновациям — это менеджер, \n"
                                                                            "курирующий отдельный проект по диджитал-трансформации. Он управляет работой бизнес-аналитиков, контролирует ход реализации проекта и отчитывается за его результат перед руководством.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 300 000 – 700 000 ₽/мес"
                                                                            "\nКак и менеджер по инновациям, это не новая позиция, а новое название старой позиции. Человек в роли директора по инновациям (или директора по диджитал-трансформации) отвечает за весь блок внедрения новых технологий в бизнес. \n"
                                                                            "Обычно он же является главой диджитал офиса, если таковой есть в компании, и напрямую подчиняется CEO. Закономерно такая позиция чаще встречается в более консервативных отраслях (промышленность, фармацевтика, FMCG).")
            if code == '~':
                await bot.send_message(callback_query.from_user.id,
                                       'Системное администрирование — направление в IT, которое обеспечивает работу компьютерной техники, сети и программного обеспечения в организации, а также совместно с подразделением кибер-безопасности отвечает за информационную безопасность компании.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/sistemnoe-administrirovanie/'
                                       '\nГде можно получить навыки для данной профессии:'
                                       '\nВысшее образование:'
                                       '\nhttp://rsreu.ru/faculties/fvt/kafedri/evm/menu-502/230100-informatika-i-vychislitelnaya-tekhnika'
                                       '\nСреднее профессиональное образование:'
                                       '\nhttps://rgtc.ru/abiturientam/otdeleniya/otdelenie-informaczionnyix-texnologij/09.02.06-setevoe-i-sistemnoe-administrirovanie.html'
                                       '\nhttps://новый.ркэ.рф/assets/%D0%9F%D0%9A/spec/%D0%A1%D0%A1%D0%90.pdf')

                buta1 = InlineKeyboardButton(text="Специалист тех.поддержки", callback_data="n*")
                buta2 = InlineKeyboardButton(text="Системный администратор", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Руководитель отдела ", callback_data="n:")
                buta4 = InlineKeyboardButton(text="IT директор", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "30 000 – 50 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 2 года"
                                                                            "\nСпециалист работает с пользователями каждый раз, когда у них что-от сломалось, не работает, глючит. \n"
                                                                            "Поэтому на начальной позиции ожидайте много общения с людьми (иногда с очень нервными людьми, которым надо, чтобы всё заработало незамедлительно).")
                    elif code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 60 000 - 120 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 4 года"
                                                                            "\nСистемный администратор в отличие от специалиста тех. поддержки может вовсе не общаться с пользователями, \n"
                                                                            "либо делать это в редких случаях. Основное его общение происходит с начальником на профессиональные темы — работа серверов, системы, почты, внедрения корпоративного ПО.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 150 000 – 250 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 6 лет"
                                                                            "\nПозиция руководителя отдела (например, руководитель отдела телефонии, сети, связи и т.д.) встречается в больших корпорациях с иерархической структурой. \n"
                                                                            "Руководитель мало самостоятельно разбирается со сломанными телефонами или «упавшими» серверами. Его задача — грамотно управлять командой сисадминов и тех.специалистов и ставить перед ними задачи.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 400 000 – 800 000 ₽/мес"
                                                                            "\nIT директор (или CIO) занимается стратегией развития внутренней информационной среды компании. Он думает над тем, какие технические решения лучше всего подойдут компании, изучает потребности коллег из других функций — маркетинга, финансов, бухгалтерии.\n"
                                                                            "А затем спускает свое видение вниз и ставит задачи младшим сотрудникам.")
            if code == '№':
                await bot.send_message(callback_query.from_user.id,
                                       'Project менеджер организует работу всей  команды таким образом, что у каждого есть понимание того, как, к какому моменту и какая задача должна быть выполнена.'
                                       '\nОн отвечает за визуализацию стратегии создания продукта, формулирует основные этапы и выстраивает последовательность достижения целей.'
                                       '\nПодробнее о примерных задачах и начальных требованиях: https://digitalway62.ru/karernye-karty/upravlenie-it-proektami/'
                                       '\nГде можно получить навыки для данной профессии:'
                                       '\nВысшее образование:'
                                       '\nhttp://rsreu.ru/faculties/fvt/kafedri/vpm/menu-504/080801-prikladnaya-informatika-v-ekonomike')
                buta1 = InlineKeyboardButton(text="Мл.Project менеджер ", callback_data="n*")
                buta2 = InlineKeyboardButton(text="Project менеджер", callback_data="n;")
                buta3 = InlineKeyboardButton(text="Старший project менеджер", callback_data="n:")
                buta4 = InlineKeyboardButton(text="Менеджер комплексного проекта", callback_data="n{")
                key = InlineKeyboardMarkup().add(buta1).insert(buta2).add(buta3).insert(buta4)
                await msg.answer("Карьерный рост", reply_markup=key)

                @dp.callback_query_handler(lambda c: c.data and c.data.startswith('n'))
                async def process_callback_kb1btn2(callback_query1: types.CallbackQuery):
                    code1 = callback_query1.data[-1]
                    if code1.isdigit():
                        code1 = int(code1)
                    if code1 == "*":
                        await bot.send_message(callback_query.from_user.id, "50 000 – 80 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 1 / 2 года"
                                                                            "\nМладший проджект помогает старшему коллеге собрать и формализовать требования к проекту. Ведёт документооборот с заказчиком и подрядчиками, \n"
                                                                            "взаимодействует с бэк-офисом (администраторами, бухгалтерией, службой поддержки). На этом этапе он учится ставить задачи разработчикам, аналитикам и другим коллегам, задействованным в создании проекта.")
                    elif code1 == ";":
                        await bot.send_message(callback_query.from_user.id, "З/П — 110 000 - 180 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 2 / 5 лет"
                                                                            "\nМенеджер способен самостоятельно вести проект средней сложности и управляет командой до 15 человек из разных департаментов. Умеет выбирать внутренних и внешних подрядчиков, участвует в пресейлах. \n"
                                                                            "Хорошо понимает бизнес заказчика. В сложные моменты умеет сплотить и смотивировать команду на решение задачи.")
                    elif code1 == ":":
                        await bot.send_message(callback_query.from_user.id, "З/П — 190 000 – 270 000 ₽/мес"
                                                                            "\nРаботает на-позиции — 3 / 6 лет"
                                                                            "\nСтаршему менеджеру доверяют более сложные проекты, где приходится вести жесткие переговоры с клиентами и управлять проектной командой 15+ человек. Участвует не только в пресейлах проектов, \n"
                                                                            "но и в их апсейлах (дополнительных продажах). В общем, это опытный управленец, который не раз был в кризисных ситуациях и умеет из них выходить.")
                    elif code1 == "{":
                        await bot.send_message(callback_query.from_user.id, "З/П — 280 000 – 350 000 ₽/мес"
                                                                            "\nХаризматичный лидер, который способен управлять проектной командой 30+ человек. Ведет самые сложные и комплексные проекты, готов быть на связи 24/7 и решать самые неприятные форс-мажорные ситуации. \n"
                                                                            "Глубоко понимает юридические и экономические риски проекта. Скилл общения с клиентом 80-го уровня.")


#Запуск
if __name__ == "__main__":
    executor.start_polling(dp)
