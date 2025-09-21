# Здесь мы импортируем библиотеки
from aiogram import Bot, types, Dispatcher, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton


#Токен(ключ) бота
bot = Bot(token="-")
dp = Dispatcher(bot, storage=MemoryStorage())


# Тут находится класс со стэйтами
class UserInfo(StatesGroup):
    numb = State()
    ss = State()
    nss = State()
    #____________
    num = State()
    ves1 = State()
    ves2 = State()



#Старотовый хэндлер
@dp.message_handler(commands='start')
async def start_cmd(msg: types.Message):
    n = msg.from_user.full_name
    await msg.answer(f'Привет, {n}!')
    await msg.answer('Я помогу тебе с решением домашних заданий по информатике, а также являюсь отличным помощником для быстрого решения задач.')
    button1 = KeyboardButton('Калькуляторы')
    button2 = KeyboardButton('Обучение')
    button3 = KeyboardButton('Помощь')
    but = ReplyKeyboardMarkup(resize_keyboard=True)
    but.add(button1).insert(button2).add(button3)
    await msg.answer('Выберите действие:', reply_markup=but)

#Хэндлер с основным функционалом
@dp.message_handler(content_types="text")
async def event(msg: types.Message):
    if msg.text == "Калькуляторы":
        button4 = KeyboardButton('Системы счисления')
        button5 = KeyboardButton('Цифровые данные')
        but1 = ReplyKeyboardMarkup(resize_keyboard=True)
        but1.add(button4).insert(button5)
        await msg.answer("Ты выбрал вкладку: Калькуляторы\nВыбери какой калькулятор тебе нужен:", reply_markup=but1)

    elif msg.text == "Системы счисления":
        await UserInfo.numb.set()
        await msg.answer('Введите число:', reply_markup=ReplyKeyboardRemove())
        @dp.message_handler(content_types='text', state=UserInfo.numb)  # Еще один хэндлер
        async def get_name(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['numb'] = msg.text
            global a
            a = int(data['numb'])
            await msg.answer(f'Ваше число: {a}\nТеперь введите систему счисления в которой находится число:')
            await UserInfo.next()

        @dp.message_handler(content_types='text', state=UserInfo.ss)  # И тут тоже
        async def get_name(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['ss'] = msg.text
            global b
            b = int(data['ss'])
            await msg.answer(f'Ваше число: {a}\nЕго система счисления: {b}\nТеперь введите систему счисления в которую хотите перенести число:')
            await UserInfo.next()

        @dp.message_handler(content_types='text', state=UserInfo.nss)  # И тут тоже
        async def get_name(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['nss'] = msg.text
            global c
            c = int(data['nss'])
            await state.finish()
            da = KeyboardButton('Подтвердить')
            but2 = ReplyKeyboardMarkup(resize_keyboard=True)
            but2.add(da)
            await msg.answer(f'Ваше число: {a}\nЕго система счисления: {b}\nТребуемая система счисления: {c}', reply_markup=but2)
    # Алгоритмы переведов сс
    if msg.text == 'Подтвердить':
        if a % 2 == 0 and a > 1:
            button1 = KeyboardButton('Калькуляторы')
            button2 = KeyboardButton('Обучение')
            button3 = KeyboardButton('Помощь')
            but = ReplyKeyboardMarkup(resize_keyboard=True)
            but.add(button1).insert(button2).add(button3)
            lis = ''
            if b == 10:
                if c == 2:
                    x = a // 2 # 5
                    o = a % 2 # 0
                    lis += str(o)
                    while x > 1:
                        if x % 2 == 0:
                            o = x - x
                            x = x // 2
                            lis += str(o)
                        elif x % 2 != 0 and x > 1:
                            o = x - (x - 1) # 1
                            x = (x - 1) // 2 # 2
                            lis += str(o)
                    lis += str(x)
                    lis = lis[::-1]
                    await msg.answer(f'Ваше новое число: {lis} в {c} системе счисления.', reply_markup=but)
            elif b == 2 and '2' not in str(a) and '3' not in str(a) and '4' not in str(a) and '5' not in str(a) and '6' not in str(a) and '7' not in str(a) and '8' not in str(a) and '9' not in str(a):
                if c == 10:
                    z = str(a)
                    k = len(z) - 1
                    m = 0
                    for i in z:
                        i = int(i) * (2 ** k)
                        k -= 1
                        m += i
                    await msg.answer(f'Ваше новое число: {m} в {c} системе счисления.', reply_markup=but)


            elif b == 8 and '8' not in str(a) and '9' not in str(a):
                if c == 10:
                    z = str(a) # 57
                    k = len(z) - 1 # 1
                    m = 0
                    for i in z:
                        i = int(i) * (8 ** k) # 40 # 7
                        k -= 1 # 0 -1
                        m += i # 40 # 47
                    await msg.answer(f'Ваше новое число: {m} в {c} системе счисления.', reply_markup=but)
            else:
                await msg.answer('Ошибка!\nПроверьте правильность введённых данных', reply_markup=but)


        elif a % 2 != 0 and a > 1:
            button1 = KeyboardButton('Калькуляторы')
            button2 = KeyboardButton('Обучение')
            button3 = KeyboardButton('Помощь')
            but = ReplyKeyboardMarkup(resize_keyboard=True)
            but.add(button1).insert(button2).add(button3)
            lis = ''
            if b == 10:
                if c == 2:
                    x = a // 2  # 7
                    o = a % 2  # 1
                    lis += str(o)
                    while x > 1:
                        if x % 2 == 0:
                            o = x - x
                            x = x // 2
                            lis += str(o)
                        elif x % 2 != 0 and x > 1:
                            o = x - (x - 1) # 1
                            x = (x - 1) // 2 # 2
                            lis += str(o)
                    lis += str(x)
                    lis = lis[::-1]
                    await msg.answer(f'Ваше новое число: {lis} в {c} системе счисления.', reply_markup=but)
            elif b == 2 and '2' not in str(a) and '3' not in str(a) and '4' not in str(a) and '5' not in str(a) and '6' not in str(a) and '7' not in str(a) and '8' not in str(a) and '9' not in str(a):
                if c == 10:
                    z = str(a)
                    k = len(z) - 1
                    m = 0
                    for i in z:
                        i = int(i) * (2 ** k)
                        k -= 1
                        m += i
                    await msg.answer(f'Ваше новое число: {m} в {c} системе счисления.', reply_markup=but)

            elif b == 8 and '8' not in str(a) and '9' not in str(a):
                if c == 10:
                    z = str(a) # 57
                    k = len(z) - 1 # 1
                    m = 0
                    for i in z:
                        i = int(i) * (8 ** k) # 40 # 7
                        k -= 1 # 0 -1
                        m += i # 40 # 47
                    await msg.answer(f'Ваше новое число: {m} в {c} системе счисления.', reply_markup=but)
            else:
                await msg.answer('Ошибка!\nПроверьте правильность введённых данных', reply_markup=but)



    if msg.text == 'Цифровые данные':
        await UserInfo.num.set()
        await msg.answer('Введите число(Вес файла):', reply_markup=ReplyKeyboardRemove())

        @dp.message_handler(content_types='text', state=UserInfo.num)  # Еще один хэндлер
        async def get_name(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['num'] = msg.text
            global aa
            aa = int(data['num'])
            butt1 = KeyboardButton('Бит')
            butt2 = KeyboardButton('Байт')
            butt3 = KeyboardButton('Килобайт')
            butt4 = KeyboardButton('Мегабайт')
            butt5 = KeyboardButton('Гигабайт')
            butt6 = KeyboardButton('Терабайт')
            but4 = ReplyKeyboardMarkup(resize_keyboard=True)
            but4.add(butt1).insert(butt2).insert(butt3).add(butt4).insert(butt5).insert(butt6)
            await msg.answer(f'Ваше число: {aa}\nВыберите единицу измерения:',reply_markup=but4)
            await UserInfo.next()

        @dp.message_handler(content_types='text', state=UserInfo.ves1)  # И тут тоже
        async def get_name(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['ves1'] = msg.text
            global bb
            bb = data['ves1']
            butt1 = KeyboardButton('Бит')
            butt2 = KeyboardButton('Байт')
            butt3 = KeyboardButton('Килобайт')
            butt4 = KeyboardButton('Мегабайт')
            butt5 = KeyboardButton('Гигабайт')
            butt6 = KeyboardButton('Терабайт')
            but4 = ReplyKeyboardMarkup(resize_keyboard=True)
            but4.add(butt1).insert(butt2).insert(butt3).add(butt4).insert(butt5).insert(butt6)
            await msg.answer(f'Ваше число: {aa}\nЕго единица измерения: {bb}\nТеперь выберите единицу измерения в которую вы хотите перевести число:',reply_markup=but4)
            await UserInfo.next()

        @dp.message_handler(content_types='text', state=UserInfo.ves2)  # И тут тоже
        async def get_name(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['ves2'] = msg.text
            global cc
            cc = (data['ves2'])
            await state.finish()
            da = KeyboardButton('Всё верно')
            but2 = ReplyKeyboardMarkup(resize_keyboard=True)
            but2.add(da)
            await msg.answer(f'Ваше число: {aa}\nЕго единица измерения: {bb}\nТребуемая единица измерения: {cc}',
                             reply_markup=but2)

    if msg.text == 'Всё верно':
        button1 = KeyboardButton('Калькуляторы')
        button2 = KeyboardButton('Обучение')
        button3 = KeyboardButton('Помощь')
        but = ReplyKeyboardMarkup(resize_keyboard=True)
        but.add(button1).insert(button2).add(button3)
        if bb == 'Бит':
            if cc == 'Байт':
                x = aa / 8
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Килобайт':
                x = aa / 8 / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Мегабайт':
                x = aa / 8 / 1024 / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Гигабайт':
                x = aa / 8 / 1024 / 1024 / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Терабайт':
                x = aa / 8 / 1024 / 1024 / 1024 / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

        elif bb == 'Байт':
            if cc == 'Бит':
                x = aa * 8
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Килобайт':
                x = aa / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Мегабайт':
                x = aa / 1024 / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Гигабайт':
                x = aa / 1024 / 1024 / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Терабайт':
                x = aa / 1024 / 1024 / 1024 / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

        elif bb == 'Килобайт':
            if cc == 'Бит':
                x = aa * 8 * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Байт':
                x = aa * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Мегабайт':
                x = aa / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Гигабайт':
                x = aa / 1024 / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Терабайт':
                x = aa / 1024 / 1024 / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

        elif bb == 'Мегабайт':
            if cc == 'Бит':
                x = aa * 8 * 1024 * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Байт':
                x = aa * 1024 * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Килобайт':
                x = aa * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Гигабайт':
                x = aa / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Терабайт':
                x = aa / 1024 / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

        elif bb == 'Гигабайт':
            if cc == 'Бит':
                x = aa * 8 * 1024 * 1024 * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Байт':
                x = aa * 1024 * 1024 * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Килобайт':
                x = aa * 1024 * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Мегабайт':
                x = aa * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Терабайт':
                x = aa / 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

        elif bb == 'Терабайт':
            if cc == 'Бит':
                x = aa * 8 * 1024 * 1024 * 1024 * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Байт':
                x = aa * 1024 * 1024 * 1024 * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Килобайт':
                x = aa * 1024 * 1024 * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Мегабайт':
                x = aa * 1024 * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

            elif cc == 'Гигабайт':
                x = aa * 1024
                await msg.answer(f'Ваше новое число: {x} {cc}.', reply_markup=but)

    if msg.text == 'Обучение':
        button7 = KeyboardButton('Перевод из разных систем счисления')
        button8 = KeyboardButton('Перевод цифровых данных')
        button9 = KeyboardButton('Языки программирования')
        but5 = ReplyKeyboardMarkup(resize_keyboard=True)
        but5.add(button7).add(button8).add(button9)
        await msg.answer('Выберите чему вы хотите научиться:', reply_markup=but5)

    if msg.text == 'Перевод из разных систем счисления':
        button1 = KeyboardButton('Калькуляторы')
        button2 = KeyboardButton('Обучение')
        button3 = KeyboardButton('Помощь')
        but = ReplyKeyboardMarkup(resize_keyboard=True)
        but.add(button1).insert(button2).add(button3)
        await msg.answer('Перевод из 10ой в 2ую\nИ перевод из 10ой в 8ую:')
        await bot.send_photo(msg.chat.id, photo='https://electro-scooterz.ru/wp-content/uploads/8/0/d/80d920f6ebda84b7ede3db7ba5b9c80c.jpeg', reply_markup=but)
        await msg.answer('Перевод из 2ой в 10ую:')
        await bot.send_photo(msg.chat.id,
                             photo='http://images.myshared.ru/9/914617/slide_8.jpg',
                             reply_markup=but)
        await msg.answer('Перевод из 8ой в 10ую:')
        await bot.send_photo(msg.chat.id,
                             photo='https://cf2.ppt-online.org/files2/slide/i/ihsyVfNm1uWZtvoa4U7RGX0Y56ApT9wbc83jSx/slide-25.jpg',
                             reply_markup=but)

    if msg.text == 'Перевод цифровых данных':
        button1 = KeyboardButton('Калькуляторы')
        button2 = KeyboardButton('Обучение')
        button3 = KeyboardButton('Помощь')
        but = ReplyKeyboardMarkup(resize_keyboard=True)
        but.add(button1).insert(button2).add(button3)
        await bot.send_photo(msg.chat.id,
                             photo='https://premudrosty.ru/wp-content/uploads/2021/06/0-0e1ea.jpg',
                             reply_markup=but)
        await bot.send_photo(msg.chat.id,
                             photo='https://cf2.ppt-online.org/files2/slide/u/UtLoFlXxWRCyOHIrA5zsN4je8kgG61abhYnK7EB0Q/slide-7.jpg',
                             reply_markup=but)
    if msg.text == 'Языки программирования':
        button1 = KeyboardButton('Калькуляторы')
        button2 = KeyboardButton('Обучение')
        button3 = KeyboardButton('Помощь')
        but = ReplyKeyboardMarkup(resize_keyboard=True)
        but.add(button1).insert(button2).add(button3)
        await msg.answer('Извините, в данный момент мы не можем загрузить этот раздел :(', reply_markup=but)

    if msg.text == 'Помощь':
        button1 = KeyboardButton('Калькуляторы')
        button2 = KeyboardButton('Обучение')
        button3 = KeyboardButton('Помощь')
        but = ReplyKeyboardMarkup(resize_keyboard=True)
        but.add(button1).insert(button2).add(button3)
        await msg.answer('Данный проект был создан: \nБессоновым Денисом\n\n Для достижения цели: \n"Помочь школьникам и обычным людям быстрее освоить азы информатики"', reply_markup=but)

#Запуск
if __name__ == "__main__":
    executor.start_polling(dp)