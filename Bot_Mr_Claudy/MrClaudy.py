from aiogram import Bot, types, Dispatcher, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton
import sys



bot = Bot(token='-')

dp = Dispatcher(bot, storage=MemoryStorage())


class UserInfo(StatesGroup):
    phot = State()
    name = State()
    description = State()
    price = State()
    identifier = State()
    name1 = State()
    description1 = State()
    price1 = State()
    identifier1 = State()
    messag = State()
    messag1 = State()


@dp.message_handler(commands='start')
async def start_cmd(msg: types.Message, state: FSMContext):
    n = msg.from_user.first_name
    await msg.answer(f'Привет, {n}!')
    button1 = KeyboardButton('Да')
    button2 = KeyboardButton('Нет')
    but = ReplyKeyboardMarkup(resize_keyboard=True)
    but.add(button1).insert(button2)
    await msg.answer('Итак, для начала нам хотелось бы узнать, есть ли тебе 18 лет?', reply_markup=but)

@dp.message_handler(content_types='text')
async def start_cmd1(msg: types.Message):
    if msg.text == 'Нет':
        keyboard1 = types.ReplyKeyboardRemove()
        await msg.reply('Извини😔, но мы работаем только с пользователями, достигшими совершеннолетия…', reply_markup=keyboard1)
    if msg.text == 'Да':
        b = KeyboardButton('Без фото📷')
        b0 = KeyboardButton('Фото📷')
        b1 = ReplyKeyboardMarkup(resize_keyboard=True)
        b1.add(b).insert(b0)
        await msg.reply('Отлично😊, начнём с фотографии. Если они необходимы, то нажми на кнопку «Фото📷» и отправь фотографию того, что ты хочешь приобрести, продать или обменять. Если же в фотографии нет необходимости, выбери кнопку «Без фото📷»',
                        reply_markup=b1)
    if msg.text == 'Фото📷':
        keyb1 = types.ReplyKeyboardRemove()
        await msg.reply('Как скажешь, ожидаю😁', reply_markup=keyb1)
        await UserInfo.phot.set()
        @dp.message_handler(content_types='photo', state=UserInfo.phot)
        async def get_photo(msg: types.chat_photo, state: FSMContext):
            # можно записать как await state.update_data(name = msg.text)
            async with state.proxy() as data:
                data['phot'] = msg.photo[-3].file_id
            global e
            e = msg.photo[-3].file_id
            await msg.answer('Так-с🤔, теперь мне нужно название того, что тебе необходимо')
            await UserInfo.next()


        @dp.message_handler(content_types='text', state=UserInfo.name)
        async def get_name(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['name'] = msg.text
            global z0
            z0 = msg.text
            await msg.answer('Угу🙃, теперь жду описание. Например, если хочешь продать устройство, то укажи его состояние («9/10, всё работает, но есть пару царапин» или «6/10, всё хорошо, но желательно заменить испаритель»), если это жидкость, то укажи название, вкус и объём, который остался, и так далее.')
            await UserInfo.next()
            # await msg.answer(f"Вот ваше объявление\n{data['phot']}\nЛет тебе: {data['age']}")
            # await bot.send_photo(msg.chat.id, data['phot'], caption=data['name'])


        @dp.message_handler(content_types='text', state=UserInfo.description)
        async def get_descripthion(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['description'] = msg.text
            global z1
            z1 = msg.text
            await msg.answer('Что по ценам?💰\nИли же тебя интересует обмен?🤨 В этом случае напиши слово «Обмен:» и укажи название того, что тебя могло бы интересовать')
            await UserInfo.next()


        @dp.message_handler(content_types='text', state=UserInfo.price)
        async def get_price(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['price'] = msg.text
            global z2
            z2 = msg.text
            await msg.answer('Хорошо😉, теперь мне нужна короткая ссылка (это такая последовательность букв и цифр, которая начинается с @) на человека, которому будет необходимо писать по поводу объявления')
            await UserInfo.next()


        @dp.message_handler(content_types='text', state=UserInfo.identifier)
        async def ident(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['identifier'] = msg.text
            global z3
            z3 = msg.text
            # await msg.answer(f"{msg.chat.id} {data['phot']}\n{data['name']}\n{data['description']}")
            await bot.send_photo(msg.chat.id, data['phot'], caption=data['name'] + '\n\n' + data['description'] + '\n\n' + data['price'] + '\n\n' + data['identifier'])
            #await state.finish()
            button3 = KeyboardButton('Всё верно👍')
            button4 = KeyboardButton('/start')
            but1 = ReplyKeyboardMarkup(resize_keyboard=True)
            but1.add(button3).insert(button4)
            await msg.answer('Проверь, чтобы всё было правильно. После нажатия на кнопку «Всё верно👍», твоё объявление автоматически '
                             'будет отправлено в наш основной канал.\nЕсли же ты неверно заполнил объявление '
                             'и хочешь заново всё заполнить, то нажми на кнопку </start> ', reply_markup=but1)
            #await bot.send_message(chat_id='-1001872737204', text='hi')
            await state.finish()

    if msg.text == 'Без фото📷':
        keyb = types.ReplyKeyboardRemove()
        await msg.reply('Так-с🤔, теперь мне нужно название того, что тебе необходимо', reply_markup=keyb)
        await UserInfo.name1.set()
        @dp.message_handler(content_types='text', state=UserInfo.name1)
        async def get_name1(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['name1'] = msg.text
            await msg.answer(
                'Угу🙃, теперь жду описание. Например, если хочешь продать устройство, то укажи его состояние («9/10, всё работает, но есть пару царапин» или «6/10, всё хорошо, но желательно заменить испаритель»), если это жидкость, то укажи название, вкус и объём, который остался, и так далее.')
            await UserInfo.next()
            # await msg.answer(f"Вот ваше объявление\n{data['phot']}\nЛет тебе: {data['age']}")
            # await bot.send_photo(msg.chat.id, data['phot'], caption=data['name'])

        @dp.message_handler(content_types='text', state=UserInfo.description1)
        async def get_descripthion1(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['description1'] = msg.text
            await msg.answer('Что по ценам?💰\nИли же тебя интересует обмен?🤨 В этом случае напиши слово «Обмен:» и укажи название того, что тебя могло бы интересовать')
            await UserInfo.next()

        @dp.message_handler(content_types='text', state=UserInfo.price1)
        async def get_price1(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['price1'] = msg.text
            await msg.answer('Хорошо😉, теперь мне нужна короткая ссылка на человека '
                             '(это такая последовательность букв и цифр, которая начинается с @), которому будут писать заинтересованные в объявлении люди')
            await UserInfo.next()

        @dp.message_handler(content_types='text', state=UserInfo.identifier1)
        async def ident11(msg: types.Message, state: FSMContext):
            # можно записать как await state.update_data(age = msg.text)
            async with state.proxy() as data:
                data['identifier1'] = msg.text
            # await msg.answer(f"{msg.chat.id} {data['phot']}\n{data['name']}\n{data['description']}")
            global a
            a = await bot.send_message(msg.chat.id,
                                   text=data['name1'] + '\n\n' + data['description1'] + '\n\n' + data['price1'] + '\n\n' +
                                         data['identifier1'])
            '''await bot.send_message(chat_id='-1001872737204',
                                   text=data['name1'] + '\n\n' + data['description1'] + '\n\n' + data[
                                       'price1'] + '\n\n' +
                                        data['identifier1'])'''
            # await state.finish()
            button3 = KeyboardButton('Всё верно👍')
            button4 = KeyboardButton('/start')
            but1 = ReplyKeyboardMarkup(resize_keyboard=True)
            but1.add(button3).insert(button4)
            await msg.answer(
                'Проверь, чтобы всё было правильно. После нажатия на кнопку «Всё верно👍», твоё объявление автоматически '
                'будет отправлено в наш основной канал.\nЕсли же ты неверно заполнил объявление '
                'и хочешь заново всё заполнить, то нажми на кнопку </start> ', reply_markup=but1)
            # await bot.send_message(chat_id='-1001872737204', text='hi')
            await state.finish()

    if msg.text == 'Всё верно👍':
        key = types.ReplyKeyboardRemove()
        await msg.reply('Безупречно! Ты справился! Ожидай обратной связи😎', reply_markup=key)
        #await bot.send_photo(chat_id='-1001872737204', photo=e, caption=z0 + '\n\n' + z1  + '\n\n' + z2 + '\n\n' + z3)
        #await bot.send_message(chat_id='-1001872737204', text=a.text)
        try:
            await bot.send_message(chat_id='-1001623198479', text=a.text)

        except NameError:
            await bot.send_photo(chat_id='-1001623198479', photo=e,
                                 caption=z0 + '\n\n' + z1 + '\n\n' + z2 + '\n\n' + z3)



if __name__ == '__main__':
    executor.start_polling(dp)