import aiogram
import asyncio
import random
import time
import sqlite3
from datetime import timedelta
from aiogram import types
from aiogram import exceptions
from aiogram.types import message
from aiogram import Bot, types, Dispatcher, executor
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types import KeyboardButton

bot = aiogram.Bot(token='-')
dp = aiogram.Dispatcher(bot)

allowed_user_id = [1108449415, 1129234807]

balances = {}

towns = {}

last_command_executed = {}

is_update_income_running = {}

winner_name = ""

list_id = []

conn = sqlite3.connect('bot_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS balances
                  (user_id INTEGER PRIMARY KEY, balance INTEGER)''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS towns
                  (user_id INTEGER PRIMARY KEY, name TEXT, army_level INTEGER, health_level INTEGER, courp_level INTEGER, road_level INTEGER, dolar_level INTEGER, food_level INTEGER, build_level INTEGER, upgraded_income INTEGER, change_count INTEGER, change_allowed INTEGER)''')
conn.commit()

cursor.execute("CREATE TABLE IF NOT EXISTS user_income (user_id INTEGER PRIMARY KEY, income INTEGER DEFAULT 0)")
conn.commit()


@dp.message_handler(commands=['start'])
async def main_command_handler(message: aiogram.types.Message):
    user_id = message.from_user.id
    await message.answer("Добро пожаловать! Создай своё королевство и стань лучшим!\n Нажми /create")


user_steps = {}


@dp.message_handler(commands=['change'])
async def change_command_handler(message: aiogram.types.Message):
    user_id = message.from_user.id

    cursor.execute("SELECT name, change_count FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать город.")
        return

    city_name, change_count = result
    change_count = change_count if change_count else 0
    change_price = 5000 * (10 ** change_count)

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(
        types.InlineKeyboardButton("Да", callback_data="confirm_change"),
        types.InlineKeyboardButton("Нет", callback_data="cancel_change")
    )

    await message.reply(
        f"Вы точно хотите изменить название города?\n"
        f"Цена: {change_price}TSC.\n\n"
        f"Текущее имя города: {city_name}",
        reply_markup=inline_keyboard
    )

    user_steps[user_id] = 1


@dp.callback_query_handler(lambda callback_query: callback_query.data in ['confirm_change', 'cancel_change'])
async def process_change_confirmation(callback_query: aiogram.types.CallbackQuery):
    user_id = callback_query.from_user.id

    if callback_query.data == 'confirm_change':
        current_balance = get_user_balance(user_id)
        change_count = get_change_count(user_id)
        change_count = change_count if change_count else 0
        change_price = 500 * (10 ** change_count)

        if current_balance < change_price:
            await callback_query.message.edit_text("У вас недостаточно средств для изменения названия города.")
            return

        await callback_query.message.edit_text(f"Введите новое название города:")

        user_steps[user_id] = 2


@dp.message_handler(lambda message: user_steps.get(message.from_user.id) == 2)
async def process_new_city_name(message: aiogram.types.Message):
    user_id = message.from_user.id
    new_city_name = message.text.strip()

    if new_city_name:
        cursor.execute("SELECT name FROM towns WHERE LOWER(name) = LOWER(?)", (new_city_name,))
        result = cursor.fetchone()

        if result:
            await message.reply("Это название города уже занято. Пожалуйста, выберите другое название.")
            return

        current_balance = get_user_balance(user_id)
        change_count = get_change_count(user_id)
        change_count = change_count if change_count else 0
        change_price = 500 * (10 ** change_count)

        if current_balance < change_price:
            await message.reply("У вас недостаточно средств для изменения названия города.")
            return

        cursor.execute("UPDATE towns SET name=?, change_count=? WHERE user_id=?",
                       (new_city_name, change_count + 1, user_id))
        conn.commit()

        update_user_balance(user_id, -change_price)

        await message.reply(f"Название вашего города успешно изменено на {new_city_name}.")

        user_steps[user_id] = 1


def get_change_count(user_id):
    cursor.execute("SELECT change_count FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    return result[0] if result else 0


@dp.message_handler(commands=['donat'])
async def main_command_handler(message: aiogram.types.Message):
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Подробнее", url="https://t.me/RudeusNG"))
    await message.answer(
        'Донат:\n\nПокупка осуществляется в отношении 1:100.000\n(Цена и отношение могут меняться\n в зависимости от суммарного уровня вашего королевства!)\n\nЧтобы узнать подробнее нажмите на кнопку ниже👇🏻',
        reply_markup=inline_keyboard)


@dp.message_handler(commands=['JHKL'])
async def main_command_handler(message: aiogram.types.Message):
    promo_mon = 100000
    user_id = message.from_user.id

    if user_id not in list_id:
        list_id.append(user_id)
        # recipient_id = message.reply_to_message.from_user.id
        recipient_id = message.from_user.id
        update_user_balance(recipient_id, promo_mon)
        await message.answer(f"Вы получили {promo_mon}TSC.")

    else:
        await message.answer('Вы уже получали деньги с промокода!\nЖдите следующего!')
        print(list_id)


@dp.message_handler(commands=['info'])
async def main_command_handler(message: aiogram.types.Message):
    await message.answer(
        'Информация о боте:\n\nНазвание: The Sovereign’s Circle\n\nВерсия: v2.5\nДата обновления: 01.10.2023')


us_lis = []


@dp.message_handler(regexp=r'^кубик (\d+)$')
async def initiate_dice_game(message: types.Message):
    user_id = message.from_user.id
    amount = int(message.text.split()[1])

    reply_message = message.reply_to_message
    recipient = reply_message.from_user

    us_lis.append(user_id)
    us_lis.append(recipient)

    if len(us_lis) > 2:
        await message.answer('Подождите, уже играют, дождитесь своей очереди')
        return

    if not recipient:
        await message.reply("Не удалось получить информацию о пользователе.")
        return

    if recipient.id == user_id:
        await message.reply("Вы не можете играть сами с собой")
        return

    recipient_mention = recipient.get_mention(as_html=True)
    recipient_username = recipient.username
    if not recipient_username:
        recipient_username = recipient.first_name

    recipient_id = recipient.id

    sender_balance = get_user_balance(user_id)
    recipient_balance = get_user_balance(recipient_id)

    if sender_balance < amount and recipient_balance > amount:
        await message.reply("Недостаточно средств для ставки.")
        del us_lis[:]
        return

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(
        types.InlineKeyboardButton("✅️Принять вызов✅️",
                                   callback_data=f"dice_challenge_accept:{amount}:{user_id}:{recipient_id}"),
        types.InlineKeyboardButton("❌️отклонить вызов❌️",
                                   callback_data=f"dice_challenge_decline:{user_id}:{recipient_id}")
    )

    await message.reply(
        f"{recipient_mention}, вас вызывают на игру в кубик!\nСумма ставки: {amount} TSC",
        reply_markup=inline_keyboard,
        parse_mode=types.ParseMode.HTML
    )

    await asyncio.sleep(20)
    await message.answer('Время на принятие решения окончено')
    del us_lis[:]


@dp.callback_query_handler(lambda c: c.data.startswith('dice_challenge_accept'))
async def accept_dice_challenge_handler(callback_query: types.CallbackQuery):
    challenge_data = callback_query.data.split(":")
    amount = int(challenge_data[1])
    challenger_id = int(challenge_data[2])
    recipient_id = int(challenge_data[3])
    challenger = await bot.get_chat_member(chat_id=callback_query.message.chat.id, user_id=challenger_id)
    recipient = await bot.get_chat_member(chat_id=callback_query.message.chat.id, user_id=recipient_id)

    if callback_query.from_user.id != recipient_id:
        await callback_query.answer("Не вам вызов!", show_alert=True)
        return
    await callback_query.message.delete()

    floe_message = await bot.send_message(chat_id=callback_query.message.chat.id, text="Игра начинается...")
    floe_message_id = floe_message.message_id

    await asyncio.sleep(1)

    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=floe_message_id)

    recipient_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                               text=f"{challenger.user.mention} бросает кубик...",
                                               parse_mode=types.ParseMode.HTML)
    recipient_message_id = recipient_message.message_id

    user_data = await bot.send_dice(chat_id=callback_query.message.chat.id, emoji="🎲",
                                    reply_to_message_id=callback_query.message.reply_to_message.message_id)
    dice_result_recipient = user_data['dice']['value']

    await asyncio.sleep(4)

    challenger_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                text=f"{recipient.user.mention} бросает кубик...")
    challenger_message_id = challenger_message.message_id

    user_data = await bot.send_dice(chat_id=callback_query.message.chat.id, emoji="🎲")
    dice_result_challenger = user_data['dice']['value']

    await asyncio.sleep(4)

    if dice_result_challenger > dice_result_recipient:
        update_user_balance(challenger_id, -amount)
        update_user_balance(recipient_id, amount)
        winner_user = challenger.user
    elif dice_result_challenger < dice_result_recipient:
        update_user_balance(challenger_id, amount)
        update_user_balance(recipient_id, -amount)
        winner_user = recipient.user
    else:
        winner_user = None

    if winner_user:
        await callback_query.message.answer(f"{winner_user.first_name} проиграл!", parse_mode=types.ParseMode.HTML)
    else:
        await callback_query.message.answer("Ничья!")

    del us_lis[:]


@dp.callback_query_handler(lambda c: c.data.startswith('dice_challenge_decline'))
async def decline_dice_challenge_handler(callback_query: types.CallbackQuery):
    challenge_data = callback_query.data.split(":")
    user_id = int(challenge_data[1])
    recipient_id = int(challenge_data[2])

    if callback_query.from_user.id != recipient_id:
        await callback_query.answer("Не вам вызов!", show_alert=True)
        return

    await callback_query.message.delete()

    await callback_query.message.answer(f"{callback_query.from_user.first_name} отклонил вызов")

    del us_lis[:]


@dp.message_handler(commands=['help'])
async def main_command_handler(message: aiogram.types.Message):
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Помощь", url="https://t.me/RudeusNG"))

    await message.answer("По всем вопросам писать администраторам группы\nЛибо менеджеру @RudeusNG",
                         reply_markup=inline_keyboard)


@dp.message_handler(commands=['game'])
async def main_command_handler(message: aiogram.types.Message):
    await message.answer(
        'В данный момент добавлены лишь Кубик*\nЧтобы сыграть *Ответьте на сообщение игрока против, котрого хотите сыграть - напишите\n *Кубик СУММА*')


@dp.message_handler(commands=['remove'])
async def main_command_handler(message: aiogram.types.Message):
    await message.answer('Чтобы вернуть кнопки нажмите на /start', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands=['rules'])
async def main_command_handler(message: aiogram.types.Message):
    await message.answer(
        'Всем, привет!\nЭто The Sovereigns Circle Bot\nИгровой бот в котором нет ограничений!!!!\nПравила просты!\nВеселиться и получать удовольствие от бота)\n'
        '\nВ боте есть простые кнопки, по которым будет понятно, что к чему\n'
        '\nКнопка /kingdom, нужна, чтобы посмотреть своё королевство, собирать казну и улучшать характеристики\n'
        '\nКнопка /farm, для сбора денег, сумма денег выпадает рандомно)\n'
        '\nКнопка /balance, чтобы узнать на сколько вы богаты ;)\n'
        '\nВ кнопке /game мы добавим разные развлекаловки, чтобы с весельем проводить время)\n'

        '\nВ кнопке Помощь ссылка для перехода, чтобы задать вопросы)\n'
        '\nЧтобы передать деньги: (*Ответьте на сообщение тому, кому хотите передать денег с текстом - *Передать СУММА**'
        '\nВсем приятной игры)\n'
        '\nЕсли у кого-то есть идеи по улучшению бота - пишите администраторам перейдя по кнопке Помощь\n'
        'Либо менеджеру @RudeusNG')


@dp.message_handler(regexp=r'^выдать (\d+)$')
async def give_command_handler(message: types.Message):
    user_id = message.from_user.id

    if user_id not in allowed_user_id or not message.reply_to_message:
        await message.answer()
        return

    try:
        amount = int(message.text.split()[1])
    except (ValueError, IndexError):
        await message.answer()
        return

    if amount <= 0:
        await message.answer()
        return

    recipient_id = message.reply_to_message.from_user.id
    update_user_balance(recipient_id, amount)
    await message.answer(f"Вы выдали {amount}TSC пользователю.")


@dp.message_handler(regexp=r'^снять (\d+)$')
async def give_command_handler(message: types.Message):
    user_id = message.from_user.id

    if user_id not in allowed_user_id or not message.reply_to_message:
        await message.answer()
        return

    try:
        amount = int(message.text.split()[1])
    except (ValueError, IndexError):
        await message.answer()
        return

    if amount <= 0:
        await message.answer()
        return

    recipient_id = message.reply_to_message.from_user.id
    update_user_balance(recipient_id, -amount)
    await message.answer(f"Вы сняли {amount}TSC пользователю.")


@dp.message_handler(commands=['farm'])
async def main_command_handler(message: aiogram.types.Message):
    user_id = message.from_user.id

    last_mine_command_time = get_last_mine_command_time(user_id)
    current_time = time.time()

    if current_time - last_mine_command_time < 60 * 60:
        time_left = timedelta(seconds=(60 * 60) - (current_time - last_mine_command_time))
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        seconds = time_left.seconds % 60
        await message.reply(
            f"Вы можете использовать команду /farm только раз в 1 час.\n Осталось {minutes} мин. {seconds} сек.")
    else:
        new_balance = random.randint(50, 300)

        update_user_balance(user_id, new_balance)

        save_last_mine_command_time(user_id, current_time)

        await message.reply(f"Вы получили {new_balance}TSC")


@dp.message_handler(commands=['balance'])
async def balance_command_handler(message: types.Message):
    user_id = message.from_user.id
    current_balance = get_user_balance(user_id)
    await message.reply(f"Ваш текущий баланс: {current_balance}TSC.")


@dp.message_handler(regexp=r'^передать (\d+)$')
async def transfer_command_handler(message: aiogram.types.Message):
    user_id = message.from_user.id
    amount = int(message.text.split()[1])

    reply_message = message.reply_to_message

    if not reply_message or reply_message.from_user.id == user_id:
        await message.reply()
        return

    recipient_id = reply_message.from_user.id

    if amount <= 0:
        await message.reply("У вас недостаточно средств для перевода.")
        return

    sender_balance = get_user_balance(user_id)
    if sender_balance < amount:
        await message.reply("У вас недостаточно средств для перевода.")
        return

    update_user_balance(user_id, -amount)
    update_user_balance(recipient_id, amount)

    await message.reply(f"Вы отправили {amount}TSC.")


@dp.message_handler(commands=['top'])
async def top_command_handler(message: types.Message):
    user_id = message.from_user.id

    cursor.execute(
        "SELECT b.user_id, b.balance, t.name FROM balances AS b JOIN towns AS t ON b.user_id = t.user_id ORDER BY b.balance DESC LIMIT 12")
    top_users = cursor.fetchall()

    top_message = "Топ 10 игроков:\n\n"
    for index, (user_id, balance, town_name) in enumerate(top_users, start=1):
        user = await bot.get_chat_member(message.chat.id, user_id)
        first_name = user.user.first_name
        if user_id in allowed_user_id:
            continue

        else:
            top_message += f"{index - 2}) Владелец: {first_name}\n Город: {town_name} \n {balance} TSC\n\n"

    await message.reply(top_message, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['create'])
async def create_command_handler(message: aiogram.types.Message):
    user_id = message.from_user.id
    if user_id == 5266482566 or user_id == 5707895629:
        await message.answer('Вам отказано в доступе!)')
    else:

        cursor.execute("SELECT name FROM towns WHERE user_id=?", (user_id,))
        result = cursor.fetchone()

        if result:
            await message.reply(
                "Вы уже создали королевство.\n Используйте команду /kingdom, чтобы узнать информацию о вашем королевстве.")
            return

        await message.reply("Создайте название для вашего королевства.")

        dp.register_message_handler(process_city_name, lambda message: message.from_user.id == user_id)


async def process_city_name(message: aiogram.types.Message):
    user_id = message.from_user.id
    city_name = message.text

    cursor.execute("INSERT INTO towns (user_id, name) VALUES (?, ?)", (user_id, city_name))
    conn.commit()

    await message.reply(
        "Ваше королевство успешно создано, нажмите на команду /kingdom чтобы посмотреть на своё королевство, желаем удачи!")


@dp.message_handler(commands=['kingdom'])
async def town_command_handler(message: aiogram.types.Message):
    user_id = message.from_user.id

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await message.answer(text, reply_markup=inline_keyboard)
    asyncio.create_task(update_income_task(user_id))


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_road')
async def upgrade_road_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()
    if result:
        city_name = result[0]
        army_level = result[1]
        health_level = result[2]
        courp_level = result[3]
        road_level = result[4]
        dolar_level = result[5]
        food_level = result[6]
        build_level = result[7]
    else:
        await callback_query.message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    if road_level is not None:
        new_road_level = road_level + 1
    else:
        new_road_level = 1

    upgrade_cost = 500 * (2 ** (new_road_level - 1))

    current_road_income_5s = 1 * (2 ** road_level) if road_level is not None else 0

    upgraded_road_income_5s = 1 * (2 ** new_road_level) if new_road_level is not None else 0

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_roads"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: ⚔️Войско\nУровень: {road_level if road_level is not None else 0}\n\nДоход в час: {current_road_income_5s}TSC\nДоход в час после улучшения: {upgraded_road_income_5s}TSC\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_dolar')
async def upgrade_dolar_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()
    if result:
        city_name = result[0]
        army_level = result[1]
        health_level = result[2]
        courp_level = result[3]
        road_level = result[4]
        dolar_level = result[5]
        food_level = result[6]
        build_level = result[7]
    else:
        await callback_query.message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    if dolar_level is not None:
        new_dolar_level = courp_level + 1
    else:
        new_dolar_level = 1

    upgrade_cost = 500 * (2 ** (new_dolar_level - 1))

    current_dolar_income_5s = 1 * (2 ** dolar_level) if dolar_level is not None else 0

    upgraded_dolar_income_5s = 1 * (2 ** new_dolar_level) if new_dolar_level is not None else 0

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_dolars"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: 📈Экономика\nУровень: {dolar_level if dolar_level is not None else 0}\n\nДоход в час: {current_dolar_income_5s}TSC\nДоход в час после улучшения: {upgraded_dolar_income_5s}TSC\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_food')
async def upgrade_food_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()
    if result:
        city_name = result[0]
        army_level = result[1]
        health_level = result[2]
        courp_level = result[3]
        road_level = result[4]
        dolar_level = result[5]
        food_level = result[6]
        build_level = result[7]
    else:
        await callback_query.message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    if food_level is not None:
        new_food_level = food_level + 1
    else:
        new_food_level = 1

    upgrade_cost = 500 * (2 ** (new_food_level - 1))

    current_food_income_5s = 1 * (2 ** food_level) if food_level is not None else 0

    upgraded_food_income_5s = 1 * (2 ** new_food_level) if new_food_level is not None else 0

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_foods"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: 🌾Сельское хозяйство\nУровень: {food_level if food_level is not None else 0}\n\nДоход в час: {current_food_income_5s}TSC\nДоход в час после улучшения: {upgraded_food_income_5s}TSC\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_build')
async def upgrade_build_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    # Обновляем время последнего выполнения команды
    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()
    if result:
        city_name = result[0]
        army_level = result[1]
        health_level = result[2]
        courp_level = result[3]
        road_level = result[4]
        dolar_level = result[5]
        food_level = result[6]
        build_level = result[7]
    else:
        await callback_query.message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    if build_level is not None:
        new_build_level = build_level + 1
    else:
        new_build_level = 1

    upgrade_cost = 500 * (2 ** (new_build_level - 1))

    current_build_income_5s = 1 * (2 ** build_level) if build_level is not None else 0

    upgraded_build_income_5s = 1 * (2 ** new_build_level) if new_build_level is not None else 0

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_builds"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: 🏫 Инфраструктура\nУровень: {build_level if build_level is not None else 0}\n\nДоход в час: {current_build_income_5s}TSC\nДоход в час после улучшения: {upgraded_build_income_5s}TSC\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_courp')
async def upgrade_courp_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()
    if result:
        city_name = result[0]
        army_level = result[1]
        health_level = result[2]
        courp_level = result[3]
        road_level = result[4]
        dolar_level = result[5]
        food_level = result[6]
        build_level = result[7]
    else:
        await callback_query.message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    if courp_level is not None:
        new_courp_level = courp_level + 1
    else:
        new_courp_level = 1

    upgrade_cost = 500 * (2 ** (new_courp_level - 1))

    current_courp_income_5s = 1 * (2 ** courp_level) if courp_level is not None else 0

    upgraded_courp_income_5s = 1 * (2 ** new_courp_level) if new_courp_level is not None else 0

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_courps"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: ⚖️Политика\nУровень: {courp_level if courp_level is not None else 0}\n\nДоход в час: {current_courp_income_5s}TSC\nДоход в час после улучшения: {upgraded_courp_income_5s}TSC\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_army')
async def upgrade_army_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level = result

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT army_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_army_level = result[0]
    else:
        current_army_level = 0

    if current_army_level is not None:
        new_army_level = current_army_level + 1
    else:
        new_army_level = 1

    upgrade_cost = 500 * (2 ** (new_army_level - 1))

    current_income_5s = 1 * (
            2 ** current_army_level) if current_army_level is not None else 0  # Текущий доход в 5 секунд
    upgraded_income_5s = 1 * (
            2 ** new_army_level) if new_army_level is not None else 0  # Доход в 5 секунд после улучшения

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_confirm"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: 🛡Защита\nУровень: {army_level if army_level is not None else 0}\n\nДоход в час: {current_income_5s}TSC\nДоход в час после улучшения: {upgraded_income_5s}$\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_health')
async def upgrade_health_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()
    if result:
        city_name = result[0]
        army_level = result[1]
        health_level = result[2]
        courp_level = result[3]
        road_level = result[4]
        dolar_level = result[5]
        food_level = result[6]
        build_level = result[7]
    else:
        await callback_query.message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    if health_level is not None:
        new_health_level = health_level + 1
    else:
        new_health_level = 1

    upgrade_cost = 500 * (2 ** (new_health_level - 1))

    current_health_income_5s = 1 * (2 ** health_level) if health_level is not None else 0

    upgraded_health_income_5s = 1 * (2 ** new_health_level) if new_health_level is not None else 0

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_healths"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: 💖Здоровье\nУровень: {health_level if health_level is not None else 0}\n\nДоход в час: {current_health_income_5s}TSC\nДоход в час после улучшения: {upgraded_health_income_5s}TSC\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'income')
async def income_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    new_balance = current_balance + income

    cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
    conn.commit()

    cursor.execute("INSERT OR REPLACE INTO user_income (user_id, income) VALUES (?, ?)", (user_id, 0))
    conn.commit()

    await callback_query.answer(f"Вы собрали доход в размере {income}TSC.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    # Обновляем время последнего выполнения команды
    last_command_executed[user_id] = time.time()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}€\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_roads')
async def upgrade_road_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_road_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT road_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET road_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_road_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня здоровья.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_dolars')
async def upgrade_dolar_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_dolar_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    # Обновляем время последнего выполнения команды
    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT dolar_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET dolar_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_dolar_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня здоровья.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_foods')
async def upgrade_food_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_food_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT food_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET food_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_food_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня здоровья.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_builds')
async def upgrade_build_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_build_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT build_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET build_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_build_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня здоровья.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_courps')
async def upgrade_courp_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_courp_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    # Обновляем время последнего выполнения команды
    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT courp_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET courp_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_courp_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня здоровья.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_healths')
async def upgrade_health_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_health_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT health_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET health_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_health_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня здоровья.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_confirm')
async def upgrade_army_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_army_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT army_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET army_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_army_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня армии.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda c: c.data == 'back_town')
async def back_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


async def update_income(user_id: int):
    while True:
        cursor.execute(
            "SELECT army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level FROM towns WHERE user_id=?",
            (user_id,))
        result = cursor.fetchone()

        if result:
            current_army_level = result[0]
            current_health_level = result[1]
            current_courp_level = result[2]
            current_road_level = result[3]
            current_dolar_level = result[4]
            current_food_level = result[5]
            current_build_level = result[6]
        else:
            current_army_level = None
            current_health_level = None
            current_courp_level = None
            current_road_level = None
            current_dolar_level = None
            current_food_level = None
            current_build_level = None

        army_income = 1 * (2 ** current_army_level) if current_army_level is not None else 0
        health_income = 1 * (2 ** current_health_level) if current_health_level is not None else 0
        courp_income = 1 * (2 ** current_courp_level) if current_courp_level is not None else 0
        road_income = 1 * (2 ** current_road_level) if current_road_level is not None else 0
        dolar_income = 1 * (2 ** current_dolar_level) if current_dolar_level is not None else 0
        food_income = 1 * (2 ** current_food_level) if current_food_level is not None else 0
        build_income = 1 * (2 ** current_build_level) if current_build_level is not None else 0

        current_income = army_income + health_income + courp_income + road_income + dolar_income + food_income + build_income

        cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        if result:
            income = result[0]
        else:
            income = 0

        new_income = income + current_income

        cursor.execute("INSERT OR REPLACE INTO user_income (user_id, income) VALUES (?, ?)", (user_id, new_income))
        conn.commit()

        upgraded_army_income = 2 * (2 ** (current_army_level + 1)) if current_army_level is not None else 0
        upgraded_health_income = 2 * (2 ** (current_health_level + 1)) if current_health_level is not None else 0
        upgraded_courp_income = 2 * (2 ** (current_courp_level + 1)) if current_courp_level is not None else 0
        upgraded_road_income = 2 * (2 ** (current_road_level + 1)) if current_road_level is not None else 0
        upgraded_dolar_income = 2 * (2 ** (current_dolar_level + 1)) if current_dolar_level is not None else 0
        upgraded_food_income = 2 * (2 ** (current_food_level + 1)) if current_food_level is not None else 0
        upgraded_build_income = 2 * (2 ** (current_build_level + 1)) if current_build_level is not None else 0

        upgraded_income = upgraded_army_income + upgraded_health_income + upgraded_courp_income + upgraded_road_income + upgraded_dolar_income + upgraded_food_income + upgraded_build_income

        cursor.execute("UPDATE towns SET upgraded_income=? WHERE user_id=?", (upgraded_income, user_id))
        conn.commit()

        cursor.execute("SELECT upgraded_income FROM towns WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        if result:
            current_upgraded_income = result[0]
        else:
            current_upgraded_income = 0

        if current_upgraded_income != upgraded_income:
            cursor.execute("UPDATE towns SET upgraded_income=? WHERE user_id=?", (upgraded_income, user_id))
            conn.commit()
            current_upgraded_income = upgraded_income

        hourly_income = current_income
        partial_income = int(hourly_income / 720)

        while True:
            await asyncio.sleep(5)

            cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
            result = cursor.fetchone()
            if result:
                income = result[0]
            else:
                income = 0

            new_income = income + partial_income

            cursor.execute("INSERT OR REPLACE INTO user_income (user_id, income) VALUES (?, ?)", (user_id, new_income))
            conn.commit()

            cursor.execute("SELECT upgraded_income FROM towns WHERE user_id=?", (user_id,))
            result = cursor.fetchone()

            if result:
                current_upgraded_income = result[0]
            else:
                current_upgraded_income = 0

            if current_upgraded_income != upgraded_income:
                cursor.execute("UPDATE towns SET upgraded_income=? WHERE user_id=?", (upgraded_income, user_id))
                conn.commit()

            cursor.execute(
                "SELECT army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level FROM towns WHERE user_id=?",
                (user_id,))
            result = cursor.fetchone()

            if result:
                current_army_level = result[0]
                current_health_level = result[1]
                current_courp_level = result[2]
                current_road_level = result[3]
                current_dolar_level = result[4]
                current_food_level = result[5]
                current_build_level = result[6]
            else:
                current_army_level = None
                current_health_level = None
                current_courp_level = None
                current_road_level = None
                current_dolar_level = None
                current_food_level = None
                current_build_level = None

            army_income = 1 * (2 ** current_army_level) if current_army_level is not None else 0
            health_income = 1 * (2 ** current_health_level) if current_health_level is not None else 0
            courp_income = 1 * (2 ** current_courp_level) if current_courp_level is not None else 0
            road_income = 1 * (2 ** current_road_level) if current_road_level is not None else 0
            dolar_income = 1 * (2 ** current_dolar_level) if current_dolar_level is not None else 0
            food_income = 1 * (2 ** current_food_level) if current_food_level is not None else 0
            build_income = 1 * (2 ** current_build_level) if current_build_level is not None else 0

            current_income = army_income + health_income + courp_income + road_income + dolar_income + food_income + build_income

            upgraded_army_income = 2 * (2 ** (current_army_level + 1)) if current_army_level is not None else 0
            upgraded_health_income = 2 * (2 ** (current_health_level + 1)) if current_health_level is not None else 0
            upgraded_courp_income = 2 * (2 ** (current_courp_level + 1)) if current_courp_level is not None else 0
            upgraded_road_income = 2 * (2 ** (current_road_level + 1)) if current_road_level is not None else 0
            upgraded_dolar_income = 2 * (2 ** (current_dolar_level + 1)) if current_dolar_level is not None else 0
            upgraded_food_income = 2 * (2 ** (current_food_level + 1)) if current_food_level is not None else 0
            upgraded_build_income = 2 * (2 ** (current_build_level + 1)) if current_build_level is not None else 0

            upgraded_income = upgraded_army_income + upgraded_health_income + upgraded_courp_income + upgraded_road_income + upgraded_dolar_income + upgraded_food_income + upgraded_build_income

            if upgraded_income != current_upgraded_income:
                cursor.execute("UPDATE towns SET upgraded_income=? WHERE user_id=?", (upgraded_income, user_id))
                conn.commit()
                current_upgraded_income = upgraded_income

            hourly_income = current_income
            partial_income = int(hourly_income / 720)


def update_user_balance(user_id, balance):
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS balances (user_id INTEGER PRIMARY KEY, balance TEXT)")
        cursor.execute("SELECT balance FROM balances WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        if result:
            current_balance = int(result[0])
        else:
            current_balance = 0

        new_balance = current_balance + int(balance)

        cursor.execute("INSERT OR REPLACE INTO balances (user_id, balance) VALUES (?, ?)", (user_id, str(new_balance)))
        conn.commit()


def get_user_balance(user_id):
    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return 0


def get_last_collect_time(user_id):
    return time.time() - 3600


def update_last_collect_time(user_id, timestamp):
    pass


def get_last_mine_command_time(user_id):
    return balances.get(f"{user_id}_last_mine_command_time", 0)


def save_last_mine_command_time(user_id, timestamp):
    balances[f"{user_id}_last_mine_command_time"] = timestamp


async def perform_update_income(user_id):
    global is_update_income_running

    if not is_update_income_running.get(user_id, False):
        is_update_income_running[user_id] = True
        await update_income(user_id)
        is_update_income_running[user_id] = False


async def update_income_task(user_id):
    while True:
        await perform_update_income(user_id)
        await asyncio.sleep(5)

    user_ids = get_all_user_ids()

    is_update_income_running = {}

    for user_id in user_ids:
        asyncio.create_task(update_income_task(user_id))


async def on():
    user_should_be_notified = -1001592098459
    await bot.send_message(user_should_be_notified, 'Бот перезагрузился...#restart\n\n@RudeusNG @FremanMQ')
    while True:
        await bot.send_message(chat_id='-1001592098459', text='Сервер активен...')
        await asyncio.sleep(120)


keep_alive()
if __name__ == '__main__':
    on_start = asyncio.get_event_loop()
    on_start.create_task(on())
    asyncio.run(aiogram.executor.start_polling(dp, skip_updates=True))
    loop = asyncio.get_event_loop()
    loop.create_task(perform_update_income())
    executor.start_polling(dp, skip_updates=True)import aiogram
import asyncio
import random
import time
import sqlite3
import aiocron
from datetime import timedelta
from aiogram import types
from aiogram import exceptions
from aiogram.types import message
from aiogram import Bot, types, Dispatcher, executor
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types import KeyboardButton
from bg import keep_alive

bot = aiogram.Bot(token='6421925198:AAHPGXJU6U9LwnvA5C_GHK3iLwlTsl3Fdds')
dp = aiogram.Dispatcher(bot)

allowed_user_id = [1108449415, 1129234807]

balances = {}

towns = {}

last_command_executed = {}

is_update_income_running = {}

winner_name = ""

list_id = []

conn = sqlite3.connect('bot_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS balances
                  (user_id INTEGER PRIMARY KEY, balance INTEGER)''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS towns
                  (user_id INTEGER PRIMARY KEY, name TEXT, army_level INTEGER, health_level INTEGER, courp_level INTEGER, road_level INTEGER, dolar_level INTEGER, food_level INTEGER, build_level INTEGER, upgraded_income INTEGER, change_count INTEGER, change_allowed INTEGER)''')
conn.commit()

cursor.execute("CREATE TABLE IF NOT EXISTS user_income (user_id INTEGER PRIMARY KEY, income INTEGER DEFAULT 0)")
conn.commit()


@dp.message_handler(commands=['start'])
async def main_command_handler(message: aiogram.types.Message):
    user_id = message.from_user.id
    await message.answer("Добро пожаловать! Создай своё королевство и стань лучшим!\n Нажми /create")

user_steps = {}

@dp.message_handler(commands=['change'])
async def change_command_handler(message: aiogram.types.Message):
    user_id = message.from_user.id

    cursor.execute("SELECT name, change_count FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать город.")
        return

    city_name, change_count = result
    change_count = change_count if change_count else 0
    change_price = 5000 * (10 ** change_count)

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(
        types.InlineKeyboardButton("Да", callback_data="confirm_change"),
        types.InlineKeyboardButton("Нет", callback_data="cancel_change")
    )

    await message.reply(
        f"Вы точно хотите изменить название города?\n"
        f"Цена: {change_price}TSC.\n\n"
        f"Текущее имя города: {city_name}",
        reply_markup=inline_keyboard
    )

    user_steps[user_id] = 1

@dp.callback_query_handler(lambda callback_query: callback_query.data in ['confirm_change', 'cancel_change'])
async def process_change_confirmation(callback_query: aiogram.types.CallbackQuery):
    user_id = callback_query.from_user.id

    if callback_query.data == 'confirm_change':
        current_balance = get_user_balance(user_id)
        change_count = get_change_count(user_id)
        change_count = change_count if change_count else 0
        change_price = 500 * (10 ** change_count)

        if current_balance < change_price:
            await callback_query.message.edit_text("У вас недостаточно средств для изменения названия города.")
            return

        await callback_query.message.edit_text(f"Введите новое название города:")

        user_steps[user_id] = 2

@dp.message_handler(lambda message: user_steps.get(message.from_user.id) == 2)
async def process_new_city_name(message: aiogram.types.Message):
    user_id = message.from_user.id
    new_city_name = message.text.strip()

    if new_city_name:
        cursor.execute("SELECT name FROM towns WHERE LOWER(name) = LOWER(?)", (new_city_name,))
        result = cursor.fetchone()

        if result:
            await message.reply("Это название города уже занято. Пожалуйста, выберите другое название.")
            return

        current_balance = get_user_balance(user_id)
        change_count = get_change_count(user_id)
        change_count = change_count if change_count else 0
        change_price = 500 * (10 ** change_count)

        if current_balance < change_price:
            await message.reply("У вас недостаточно средств для изменения названия города.")
            return

        cursor.execute("UPDATE towns SET name=?, change_count=? WHERE user_id=?", (new_city_name, change_count + 1, user_id))
        conn.commit()

        update_user_balance(user_id, -change_price)

        await message.reply(f"Название вашего города успешно изменено на {new_city_name}.")

        user_steps[user_id] = 1

def get_change_count(user_id):
    cursor.execute("SELECT change_count FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    return result[0] if result else 0



@dp.message_handler(commands=['donat'])
async def main_command_handler(message: aiogram.types.Message):
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Подробнее", url="https://t.me/RudeusNG"))
    await message.answer('Донат:\n\nПокупка осуществляется в отношении 1:100.000\n(Цена и отношение могут меняться\n в зависимости от суммарного уровня вашего королевства!)\n\nЧтобы узнать подробнее нажмите на кнопку ниже👇🏻', reply_markup=inline_keyboard)

@dp.message_handler(commands=['JHKL'])
async def main_command_handler(message: aiogram.types.Message):
    promo_mon = 100000
    user_id = message.from_user.id

    if user_id not in list_id:
        list_id.append(user_id)
        #recipient_id = message.reply_to_message.from_user.id
        recipient_id = message.from_user.id
        update_user_balance(recipient_id, promo_mon)
        await message.answer(f"Вы получили {promo_mon}TSC.")

    else:
        await message.answer('Вы уже получали деньги с промокода!\nЖдите следующего!')
        print(list_id)

@dp.message_handler(commands=['info'])
async def main_command_handler(message: aiogram.types.Message):
    await message.answer('Информация о боте:\n\nНазвание: The Sovereign’s Circle\n\nВерсия: v2.5\nДата обновления: 01.10.2023')


us_lis = []

@dp.message_handler(regexp=r'^кубик (\d+)$')
async def initiate_dice_game(message: types.Message):
    user_id = message.from_user.id
    amount = int(message.text.split()[1])

    reply_message = message.reply_to_message
    recipient = reply_message.from_user

    us_lis.append(user_id)
    us_lis.append(recipient)

    if len(us_lis) > 2:
        await message.answer('Подождите, уже играют, дождитесь своей очереди')
        return

    if not recipient:
        await message.reply("Не удалось получить информацию о пользователе.")
        return

    if recipient.id == user_id:
        await message.reply("Вы не можете играть сами с собой")
        return

    recipient_mention = recipient.get_mention(as_html=True)
    recipient_username = recipient.username
    if not recipient_username:
        recipient_username = recipient.first_name

    recipient_id = recipient.id

    sender_balance = get_user_balance(user_id)
    recipient_balance = get_user_balance(recipient_id)

    if sender_balance < amount and recipient_balance > amount:
        await message.reply("Недостаточно средств для ставки.")
        del us_lis[:]
        return

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(
        types.InlineKeyboardButton("✅️Принять вызов✅️",
                                   callback_data=f"dice_challenge_accept:{amount}:{user_id}:{recipient_id}"),
        types.InlineKeyboardButton("❌️отклонить вызов❌️",
                                   callback_data=f"dice_challenge_decline:{user_id}:{recipient_id}")
    )

    await message.reply(
    f"{recipient_mention}, вас вызывают на игру в кубик!\nСумма ставки: {amount} TSC",
                                         reply_markup=inline_keyboard,
                                         parse_mode=types.ParseMode.HTML
                                         )

    await asyncio.sleep(20)
    await message.answer('Время на принятие решения окончено')
    del us_lis[:]


@dp.callback_query_handler(lambda c: c.data.startswith('dice_challenge_accept'))
async def accept_dice_challenge_handler(callback_query: types.CallbackQuery):
    challenge_data = callback_query.data.split(":")
    amount = int(challenge_data[1])
    challenger_id = int(challenge_data[2])
    recipient_id = int(challenge_data[3])
    challenger = await bot.get_chat_member(chat_id=callback_query.message.chat.id, user_id=challenger_id)
    recipient = await bot.get_chat_member(chat_id=callback_query.message.chat.id, user_id=recipient_id)

    if callback_query.from_user.id != recipient_id:
        await callback_query.answer("Не вам вызов!", show_alert=True)
        return
    await callback_query.message.delete()


    floe_message = await bot.send_message(chat_id=callback_query.message.chat.id, text="Игра начинается...")
    floe_message_id = floe_message.message_id

    await asyncio.sleep(1)

    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=floe_message_id)

    recipient_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                               text=f"{challenger.user.mention} бросает кубик...",
                                               parse_mode=types.ParseMode.HTML)
    recipient_message_id = recipient_message.message_id

    user_data = await bot.send_dice(chat_id=callback_query.message.chat.id, emoji="🎲",
                                    reply_to_message_id=callback_query.message.reply_to_message.message_id)
    dice_result_recipient = user_data['dice']['value']

    await asyncio.sleep(4)

    challenger_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                text=f"{recipient.user.mention} бросает кубик...")
    challenger_message_id = challenger_message.message_id

    user_data = await bot.send_dice(chat_id=callback_query.message.chat.id, emoji="🎲")
    dice_result_challenger = user_data['dice']['value']

    await asyncio.sleep(4)

    if dice_result_challenger > dice_result_recipient:
        update_user_balance(challenger_id, -amount)
        update_user_balance(recipient_id, amount)
        winner_user = challenger.user
    elif dice_result_challenger < dice_result_recipient:
        update_user_balance(challenger_id, amount)
        update_user_balance(recipient_id, -amount)
        winner_user = recipient.user
    else:
        winner_user = None

    if winner_user:
        await callback_query.message.answer(f"{winner_user.first_name} проиграл!", parse_mode=types.ParseMode.HTML)
    else:
        await callback_query.message.answer("Ничья!")

    del us_lis[:]


@dp.callback_query_handler(lambda c: c.data.startswith('dice_challenge_decline'))
async def decline_dice_challenge_handler(callback_query: types.CallbackQuery):
    challenge_data = callback_query.data.split(":")
    user_id = int(challenge_data[1])
    recipient_id = int(challenge_data[2])

    if callback_query.from_user.id != recipient_id:
        await callback_query.answer("Не вам вызов!", show_alert=True)
        return

    await callback_query.message.delete()

    await callback_query.message.answer(f"{callback_query.from_user.first_name} отклонил вызов")

    del us_lis[:]


@dp.message_handler(commands=['help'])
async def main_command_handler(message: aiogram.types.Message):
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Помощь", url="https://t.me/RudeusNG"))

    await message.answer("По всем вопросам писать администраторам группы\nЛибо менеджеру @RudeusNG", reply_markup=inline_keyboard)

@dp.message_handler(commands=['game'])
async def main_command_handler(message: aiogram.types.Message):
  await message.answer('В данный момент добавлены лишь Кубик*\nЧтобы сыграть *Ответьте на сообщение игрока против, котрого хотите сыграть - напишите\n *Кубик СУММА*')

@dp.message_handler(commands=['remove'])
async def main_command_handler(message: aiogram.types.Message):
    await message.answer('Чтобы вернуть кнопки нажмите на /start', reply_markup=ReplyKeyboardRemove())

@dp.message_handler(commands=['rules'])
async def main_command_handler(message: aiogram.types.Message):
    await message.answer('Всем, привет!\nЭто The Sovereigns Circle Bot\nИгровой бот в котором нет ограничений!!!!\nПравила просты!\nВеселиться и получать удовольствие от бота)\n'
                         '\nВ боте есть простые кнопки, по которым будет понятно, что к чему\n'
                         '\nКнопка /kingdom, нужна, чтобы посмотреть своё королевство, собирать казну и улучшать характеристики\n'
                         '\nКнопка /farm, для сбора денег, сумма денег выпадает рандомно)\n'
                         '\nКнопка /balance, чтобы узнать на сколько вы богаты ;)\n'
                         '\nВ кнопке /game мы добавим разные развлекаловки, чтобы с весельем проводить время)\n'
                        
                         '\nВ кнопке Помощь ссылка для перехода, чтобы задать вопросы)\n'
                         '\nЧтобы передать деньги: (*Ответьте на сообщение тому, кому хотите передать денег с текстом - *Передать СУММА**'
                         '\nВсем приятной игры)\n'
                         '\nЕсли у кого-то есть идеи по улучшению бота - пишите администраторам перейдя по кнопке Помощь\n'
                         'Либо менеджеру @RudeusNG')

@dp.message_handler(regexp=r'^выдать (\d+)$')
async def give_command_handler(message: types.Message):
    user_id = message.from_user.id

    if user_id not in allowed_user_id or not message.reply_to_message:
        await message.answer()
        return

    try:
        amount = int(message.text.split()[1])
    except (ValueError, IndexError):
        await message.answer()
        return

    if amount <= 0:
        await message.answer()
        return

    recipient_id = message.reply_to_message.from_user.id
    update_user_balance(recipient_id, amount)
    await message.answer(f"Вы выдали {amount}TSC пользователю.")


@dp.message_handler(regexp=r'^снять (\d+)$')
async def give_command_handler(message: types.Message):
    user_id = message.from_user.id

    if user_id not in allowed_user_id or not message.reply_to_message:
        await message.answer()
        return

    try:
        amount = int(message.text.split()[1])
    except (ValueError, IndexError):
        await message.answer()
        return

    if amount <= 0:
        await message.answer()
        return

    recipient_id = message.reply_to_message.from_user.id
    update_user_balance(recipient_id, -amount)
    await message.answer(f"Вы сняли {amount}TSC пользователю.")


@dp.message_handler(commands=['farm'])
async def main_command_handler(message: aiogram.types.Message):
    user_id = message.from_user.id

    last_mine_command_time = get_last_mine_command_time(user_id)
    current_time = time.time()

    if current_time - last_mine_command_time <  60 * 60:
        time_left = timedelta(seconds=(60 * 60) - (current_time - last_mine_command_time))
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        seconds = time_left.seconds % 60
        await message.reply(
            f"Вы можете использовать команду /farm только раз в 1 час.\n Осталось {minutes} мин. {seconds} сек.")
    else:
        new_balance = random.randint(50, 300)

        update_user_balance(user_id, new_balance)

        save_last_mine_command_time(user_id, current_time)

        await message.reply(f"Вы получили {new_balance}TSC")


@dp.message_handler(commands=['balance'])
async def balance_command_handler(message: types.Message):
    user_id = message.from_user.id
    current_balance = get_user_balance(user_id)
    await message.reply(f"Ваш текущий баланс: {current_balance}TSC.")


@dp.message_handler(regexp=r'^передать (\d+)$')
async def transfer_command_handler(message: aiogram.types.Message):
    user_id = message.from_user.id
    amount = int(message.text.split()[1])

    reply_message = message.reply_to_message

    if not reply_message or reply_message.from_user.id == user_id:
        await message.reply()
        return

    recipient_id = reply_message.from_user.id

    if amount <= 0:
        await message.reply("У вас недостаточно средств для перевода.")
        return

    sender_balance = get_user_balance(user_id)
    if sender_balance < amount:
        await message.reply("У вас недостаточно средств для перевода.")
        return

    update_user_balance(user_id, -amount)
    update_user_balance(recipient_id, amount)

    await message.reply(f"Вы отправили {amount}TSC.")


@dp.message_handler(commands=['top'])
async def top_command_handler(message: types.Message):
    user_id = message.from_user.id

    cursor.execute("SELECT b.user_id, b.balance, t.name FROM balances AS b JOIN towns AS t ON b.user_id = t.user_id ORDER BY b.balance DESC LIMIT 12")
    top_users = cursor.fetchall()

    top_message = "Топ 10 игроков:\n\n"
    for index, (user_id, balance, town_name) in enumerate(top_users, start=1):
        user = await bot.get_chat_member(message.chat.id, user_id)
        first_name = user.user.first_name
        if user_id in allowed_user_id:
            continue

        else:
            top_message += f"{index-2}) Владелец: {first_name}\n Город: {town_name} \n {balance} TSC\n\n"

    await message.reply(top_message, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['create'])
async def create_command_handler(message: aiogram.types.Message):
    user_id = message.from_user.id
    if user_id == 5266482566 or user_id == 5707895629:
      await message.answer('Вам отказано в доступе!)')
    else:

      cursor.execute("SELECT name FROM towns WHERE user_id=?", (user_id,))
      result = cursor.fetchone()

      if result:
          await message.reply(
              "Вы уже создали королевство.\n Используйте команду /kingdom, чтобы узнать информацию о вашем королевстве.")
          return

      await message.reply("Создайте название для вашего королевства.")

      dp.register_message_handler(process_city_name, lambda message: message.from_user.id == user_id)


async def process_city_name(message: aiogram.types.Message):
      user_id = message.from_user.id
      city_name = message.text

      cursor.execute("INSERT INTO towns (user_id, name) VALUES (?, ?)", (user_id, city_name))
      conn.commit()

      await message.reply(
          "Ваше королевство успешно создано, нажмите на команду /kingdom чтобы посмотреть на своё королевство, желаем удачи!")


@dp.message_handler(commands=['kingdom'])
async def town_command_handler(message: aiogram.types.Message):
    user_id = message.from_user.id

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute(""
                   "balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await message.answer(text, reply_markup=inline_keyboard)
    asyncio.create_task(update_income_task(user_id))


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_road')
async def upgrade_road_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()
    if result:
        city_name = result[0]
        army_level = result[1]
        health_level = result[2]
        courp_level = result[3]
        road_level = result[4]
        dolar_level = result[5]
        food_level = result[6]
        build_level = result[7]
    else:
        await callback_query.message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    if road_level is not None:
        new_road_level = road_level + 1
    else:
        new_road_level = 1

    upgrade_cost = 500 * (2 ** (new_road_level - 1))

    current_road_income_5s = 1 * (2 ** road_level) if road_level is not None else 0

    upgraded_road_income_5s = 1 * (2 ** new_road_level) if new_road_level is not None else 0

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_roads"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: ⚔️Войско\nУровень: {road_level if road_level is not None else 0}\n\nДоход в час: {current_road_income_5s}TSC\nДоход в час после улучшения: {upgraded_road_income_5s}TSC\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_dolar')
async def upgrade_dolar_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()
    if result:
        city_name = result[0]
        army_level = result[1]
        health_level = result[2]
        courp_level = result[3]
        road_level = result[4]
        dolar_level = result[5]
        food_level = result[6]
        build_level = result[7]
    else:
        await callback_query.message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    if dolar_level is not None:
        new_dolar_level = courp_level + 1
    else:
        new_dolar_level = 1

    upgrade_cost = 500 * (2 ** (new_dolar_level - 1))

    current_dolar_income_5s = 1 * (2 ** dolar_level) if dolar_level is not None else 0

    upgraded_dolar_income_5s = 1 * (2 ** new_dolar_level) if new_dolar_level is not None else 0

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_dolars"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: 📈Экономика\nУровень: {dolar_level if dolar_level is not None else 0}\n\nДоход в час: {current_dolar_income_5s}TSC\nДоход в час после улучшения: {upgraded_dolar_income_5s}TSC\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_food')
async def upgrade_food_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()
    if result:
        city_name = result[0]
        army_level = result[1]
        health_level = result[2]
        courp_level = result[3]
        road_level = result[4]
        dolar_level = result[5]
        food_level = result[6]
        build_level = result[7]
    else:
        await callback_query.message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    if food_level is not None:
        new_food_level = food_level + 1
    else:
        new_food_level = 1

    upgrade_cost = 500 * (2 ** (new_food_level - 1))

    current_food_income_5s = 1 * (2 ** food_level) if food_level is not None else 0

    upgraded_food_income_5s = 1 * (2 ** new_food_level) if new_food_level is not None else 0

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_foods"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: 🌾Сельское хозяйство\nУровень: {food_level if food_level is not None else 0}\n\nДоход в час: {current_food_income_5s}TSC\nДоход в час после улучшения: {upgraded_food_income_5s}TSC\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_build')
async def upgrade_build_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    # Обновляем время последнего выполнения команды
    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()
    if result:
        city_name = result[0]
        army_level = result[1]
        health_level = result[2]
        courp_level = result[3]
        road_level = result[4]
        dolar_level = result[5]
        food_level = result[6]
        build_level = result[7]
    else:
        await callback_query.message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    if build_level is not None:
        new_build_level = build_level + 1
    else:
        new_build_level = 1

    upgrade_cost = 500 * (2 ** (new_build_level - 1))

    current_build_income_5s = 1 * (2 ** build_level) if build_level is not None else 0

    upgraded_build_income_5s = 1 * (2 ** new_build_level) if new_build_level is not None else 0

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_builds"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: 🏫 Инфраструктура\nУровень: {build_level if build_level is not None else 0}\n\nДоход в час: {current_build_income_5s}TSC\nДоход в час после улучшения: {upgraded_build_income_5s}TSC\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_courp')
async def upgrade_courp_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()
    if result:
        city_name = result[0]
        army_level = result[1]
        health_level = result[2]
        courp_level = result[3]
        road_level = result[4]
        dolar_level = result[5]
        food_level = result[6]
        build_level = result[7]
    else:
        await callback_query.message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    if courp_level is not None:
        new_courp_level = courp_level + 1
    else:
        new_courp_level = 1

    upgrade_cost = 500 * (2 ** (new_courp_level - 1))

    current_courp_income_5s = 1 * (2 ** courp_level) if courp_level is not None else 0

    upgraded_courp_income_5s = 1 * (2 ** new_courp_level) if new_courp_level is not None else 0

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_courps"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: ⚖️Политика\nУровень: {courp_level if courp_level is not None else 0}\n\nДоход в час: {current_courp_income_5s}TSC\nДоход в час после улучшения: {upgraded_courp_income_5s}TSC\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_army')
async def upgrade_army_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level = result

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT army_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_army_level = result[0]
    else:
        current_army_level = 0

    if current_army_level is not None:
        new_army_level = current_army_level + 1
    else:
        new_army_level = 1

    upgrade_cost = 500 * (2 ** (new_army_level - 1))

    current_income_5s = 1 * (
                2 ** current_army_level) if current_army_level is not None else 0  # Текущий доход в 5 секунд
    upgraded_income_5s = 1 * (
                2 ** new_army_level) if new_army_level is not None else 0  # Доход в 5 секунд после улучшения

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_confirm"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: 🛡Защита\nУровень: {army_level if army_level is not None else 0}\n\nДоход в час: {current_income_5s}TSC\nДоход в час после улучшения: {upgraded_income_5s}$\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_health')
async def upgrade_health_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()
    if result:
        city_name = result[0]
        army_level = result[1]
        health_level = result[2]
        courp_level = result[3]
        road_level = result[4]
        dolar_level = result[5]
        food_level = result[6]
        build_level = result[7]
    else:
        await callback_query.message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    if health_level is not None:
        new_health_level = health_level + 1
    else:
        new_health_level = 1

    upgrade_cost = 500 * (2 ** (new_health_level - 1))

    current_health_income_5s = 1 * (2 ** health_level) if health_level is not None else 0

    upgraded_health_income_5s = 1 * (2 ** new_health_level) if new_health_level is not None else 0

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(types.InlineKeyboardButton("Улучшить", callback_data="upgrade_healths"))
    inline_keyboard.add(types.InlineKeyboardButton("Назад", callback_data='back_town'))

    text = f"🏯Королевство: {city_name}\n\nПараметр: 💖Здоровье\nУровень: {health_level if health_level is not None else 0}\n\nДоход в час: {current_health_income_5s}TSC\nДоход в час после улучшения: {upgraded_health_income_5s}TSC\n\nСтоимость улучшения: {upgrade_cost}TSC\n💎TSC на счету: {current_balance}TSC"

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'income')
async def income_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    new_balance = current_balance + income

    cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
    conn.commit()

    cursor.execute("INSERT OR REPLACE INTO user_income (user_id, income) VALUES (?, ?)", (user_id, 0))
    conn.commit()

    await callback_query.answer(f"Вы собрали доход в размере {income}TSC.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    # Обновляем время последнего выполнения команды
    last_command_executed[user_id] = time.time()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}€\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_roads')
async def upgrade_road_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_road_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT road_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET road_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_road_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня здоровья.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_dolars')
async def upgrade_dolar_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_dolar_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    # Обновляем время последнего выполнения команды
    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT dolar_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET dolar_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_dolar_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня здоровья.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_foods')
async def upgrade_food_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_food_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT food_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET food_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_food_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня здоровья.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_builds')
async def upgrade_build_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_build_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT build_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET build_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_build_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня здоровья.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_courps')
async def upgrade_courp_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_courp_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    # Обновляем время последнего выполнения команды
    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT courp_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET courp_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_courp_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня здоровья.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_healths')
async def upgrade_health_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_health_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT health_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET health_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_health_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня здоровья.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'upgrade_confirm')
async def upgrade_army_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    global current_army_level

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    cursor.execute("SELECT army_level FROM towns WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_level = result[0]
    else:
        current_level = 0

    if current_level is not None:
        new_level = current_level + 1
    else:
        new_level = 1

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0

    upgrade_cost = 500 * (2 ** (new_level - 1))

    if balance >= upgrade_cost:
        if new_level <= 10000:
            cursor.execute("UPDATE towns SET army_level=? WHERE user_id=?", (new_level, user_id))
            conn.commit()

            new_balance = balance - upgrade_cost
            cursor.execute("UPDATE balances SET balance=? WHERE user_id=?", (new_balance, user_id))
            conn.commit()

            await callback_query.answer("Уровень параметра улучшен.", show_alert=True)

            current_army_level = new_level
            asyncio.create_task(perform_update_income(user_id))
        else:
            await callback_query.message.edit_text("Вы достигли максимального уровня армии.")
    else:
        await callback_query.answer("Недостаточно средств на балансе.", show_alert=True)

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level, upgraded_income = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda c: c.data == 'back_town')
async def back_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    cursor.execute(
        "SELECT name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level FROM towns WHERE user_id=?",
        (user_id,))
    result = cursor.fetchone()

    if user_id in last_command_executed:
        last_executed_time = last_command_executed[user_id]
        current_time = time.time()
        if current_time - last_executed_time < 1.5:
            await asyncio.sleep(1.5 - (current_time - last_executed_time))

    last_command_executed[user_id] = time.time()

    if not result:
        await message.reply("Сначала выполните команду /create, чтобы создать королевство.")
        return

    city_name, army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level = result

    army_level = army_level or 0
    health_level = health_level or 0
    courp_level = courp_level or 0
    road_level = road_level or 0
    dolar_level = dolar_level or 0
    food_level = food_level or 0
    build_level = build_level or 0

    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_balance = result[0]
    else:
        current_balance = 0

    cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        income = result[0]
    else:
        income = 0

    text = f"🏯Королевство: {city_name}\n\n🛡Защита: {army_level}\n💖Здоровье: {health_level}\n⚖️Политика: {courp_level}\n⚔️Войско: {road_level}\n🏫 Инфраструктура: {build_level}\n📈Экономика: {dolar_level}\n🌾Сельское хозяйство: {food_level}\n\n💰Бюджет королевства: {income}TSC\n\n💎TSC на счету: {current_balance}TSC"

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(types.InlineKeyboardButton("🛡 Защита", callback_data="upgrade_army"),
                        types.InlineKeyboardButton("💖 Здоровье", callback_data="upgrade_health"),
                        types.InlineKeyboardButton("⚖️ Политика", callback_data="upgrade_courp"))
    inline_keyboard.row(types.InlineKeyboardButton("⚔️ Войско", callback_data="upgrade_road"),
                        types.InlineKeyboardButton("🏫 Инфраструктура", callback_data="upgrade_build"),
                        types.InlineKeyboardButton("📈 Экономика", callback_data="upgrade_dolar"))
    inline_keyboard.row(types.InlineKeyboardButton("🌾 Сельское хозяйство", callback_data="upgrade_food"))
    inline_keyboard.row(types.InlineKeyboardButton(f"💰 Собрать прибыль {income}TSC", callback_data="income"))

    await callback_query.message.edit_text(text, reply_markup=inline_keyboard)


async def update_income(user_id: int):
    while True:
        cursor.execute(
            "SELECT army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level FROM towns WHERE user_id=?",
            (user_id,))
        result = cursor.fetchone()

        if result:
            current_army_level = result[0]
            current_health_level = result[1]
            current_courp_level = result[2]
            current_road_level = result[3]
            current_dolar_level = result[4]
            current_food_level = result[5]
            current_build_level = result[6]
        else:
            current_army_level = None
            current_health_level = None
            current_courp_level = None
            current_road_level = None
            current_dolar_level = None
            current_food_level = None
            current_build_level = None

        army_income = 1 * (2 ** current_army_level) if current_army_level is not None else 0
        health_income = 1 * (2 ** current_health_level) if current_health_level is not None else 0
        courp_income = 1 * (2 ** current_courp_level) if current_courp_level is not None else 0
        road_income = 1 * (2 ** current_road_level) if current_road_level is not None else 0
        dolar_income = 1 * (2 ** current_dolar_level) if current_dolar_level is not None else 0
        food_income = 1 * (2 ** current_food_level) if current_food_level is not None else 0
        build_income = 1 * (2 ** current_build_level) if current_build_level is not None else 0

        current_income = army_income + health_income + courp_income + road_income + dolar_income + food_income + build_income

        cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        if result:
            income = result[0]
        else:
            income = 0

        new_income = income + current_income

        cursor.execute("INSERT OR REPLACE INTO user_income (user_id, income) VALUES (?, ?)", (user_id, new_income))
        conn.commit()

        upgraded_army_income = 2 * (2 ** (current_army_level + 1)) if current_army_level is not None else 0
        upgraded_health_income = 2 * (2 ** (current_health_level + 1)) if current_health_level is not None else 0
        upgraded_courp_income = 2 * (2 ** (current_courp_level + 1)) if current_courp_level is not None else 0
        upgraded_road_income = 2 * (2 ** (current_road_level + 1)) if current_road_level is not None else 0
        upgraded_dolar_income = 2 * (2 ** (current_dolar_level + 1)) if current_dolar_level is not None else 0
        upgraded_food_income = 2 * (2 ** (current_food_level + 1)) if current_food_level is not None else 0
        upgraded_build_income = 2 * (2 ** (current_build_level + 1)) if current_build_level is not None else 0

        upgraded_income = upgraded_army_income + upgraded_health_income + upgraded_courp_income + upgraded_road_income + upgraded_dolar_income + upgraded_food_income + upgraded_build_income

        cursor.execute("UPDATE towns SET upgraded_income=? WHERE user_id=?", (upgraded_income, user_id))
        conn.commit()

        cursor.execute("SELECT upgraded_income FROM towns WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        if result:
            current_upgraded_income = result[0]
        else:
            current_upgraded_income = 0

        if current_upgraded_income != upgraded_income:
            cursor.execute("UPDATE towns SET upgraded_income=? WHERE user_id=?", (upgraded_income, user_id))
            conn.commit()
            current_upgraded_income = upgraded_income

        hourly_income = current_income
        partial_income = int(hourly_income / 720)

        while True:
            await asyncio.sleep(5)

            cursor.execute("SELECT income FROM user_income WHERE user_id=?", (user_id,))
            result = cursor.fetchone()
            if result:
                income = result[0]
            else:
                income = 0

            new_income = income + partial_income

            cursor.execute("INSERT OR REPLACE INTO user_income (user_id, income) VALUES (?, ?)", (user_id, new_income))
            conn.commit()

            cursor.execute("SELECT upgraded_income FROM towns WHERE user_id=?", (user_id,))
            result = cursor.fetchone()

            if result:
                current_upgraded_income = result[0]
            else:
                current_upgraded_income = 0

            if current_upgraded_income != upgraded_income:
                cursor.execute("UPDATE towns SET upgraded_income=? WHERE user_id=?", (upgraded_income, user_id))
                conn.commit()

            cursor.execute(
                "SELECT army_level, health_level, courp_level, road_level, dolar_level, food_level, build_level FROM towns WHERE user_id=?",
                (user_id,))
            result = cursor.fetchone()

            if result:
                current_army_level = result[0]
                current_health_level = result[1]
                current_courp_level = result[2]
                current_road_level = result[3]
                current_dolar_level = result[4]
                current_food_level = result[5]
                current_build_level = result[6]
            else:
                current_army_level = None
                current_health_level = None
                current_courp_level = None
                current_road_level = None
                current_dolar_level = None
                current_food_level = None
                current_build_level = None

            army_income = 1 * (2 ** current_army_level) if current_army_level is not None else 0
            health_income = 1 * (2 ** current_health_level) if current_health_level is not None else 0
            courp_income = 1 * (2 ** current_courp_level) if current_courp_level is not None else 0
            road_income = 1 * (2 ** current_road_level) if current_road_level is not None else 0
            dolar_income = 1 * (2 ** current_dolar_level) if current_dolar_level is not None else 0
            food_income = 1 * (2 ** current_food_level) if current_food_level is not None else 0
            build_income = 1 * (2 ** current_build_level) if current_build_level is not None else 0

            current_income = army_income + health_income + courp_income + road_income + dolar_income + food_income + build_income

            upgraded_army_income = 2 * (2 ** (current_army_level + 1)) if current_army_level is not None else 0
            upgraded_health_income = 2 * (2 ** (current_health_level + 1)) if current_health_level is not None else 0
            upgraded_courp_income = 2 * (2 ** (current_courp_level + 1)) if current_courp_level is not None else 0
            upgraded_road_income = 2 * (2 ** (current_road_level + 1)) if current_road_level is not None else 0
            upgraded_dolar_income = 2 * (2 ** (current_dolar_level + 1)) if current_dolar_level is not None else 0
            upgraded_food_income = 2 * (2 ** (current_food_level + 1)) if current_food_level is not None else 0
            upgraded_build_income = 2 * (2 ** (current_build_level + 1)) if current_build_level is not None else 0

            upgraded_income = upgraded_army_income + upgraded_health_income + upgraded_courp_income + upgraded_road_income + upgraded_dolar_income + upgraded_food_income + upgraded_build_income

            if upgraded_income != current_upgraded_income:
                cursor.execute("UPDATE towns SET upgraded_income=? WHERE user_id=?", (upgraded_income, user_id))
                conn.commit()
                current_upgraded_income = upgraded_income

            hourly_income = current_income
            partial_income = int(hourly_income / 720)


def update_user_balance(user_id, balance):
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS balances (user_id INTEGER PRIMARY KEY, balance TEXT)")
        cursor.execute("SELECT balance FROM balances WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        if result:
            current_balance = int(result[0])
        else:
            current_balance = 0

        new_balance = current_balance + int(balance)

        cursor.execute("INSERT OR REPLACE INTO balances (user_id, balance) VALUES (?, ?)", (user_id, str(new_balance)))
        conn.commit()


def get_user_balance(user_id):
    cursor.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return 0


def get_last_collect_time(user_id):
    return time.time() - 3600


def update_last_collect_time(user_id, timestamp):
    pass


def get_last_mine_command_time(user_id):
    return balances.get(f"{user_id}_last_mine_command_time", 0)


def save_last_mine_command_time(user_id, timestamp):
    balances[f"{user_id}_last_mine_command_time"] = timestamp


async def perform_update_income(user_id):
    global is_update_income_running

    if not is_update_income_running.get(user_id, False):
        is_update_income_running[user_id] = True
        await update_income(user_id)
        is_update_income_running[user_id] = False


async def update_income_task(user_id):
    while True:
        await perform_update_income(user_id)
        await asyncio.sleep(5)

    user_ids = get_all_user_ids()

    is_update_income_running = {}

    for user_id in user_ids:
        asyncio.create_task(update_income_task(user_id))



async def on():
    user_should_be_notified = -1001592098459
    await bot.send_message(user_should_be_notified, 'Бот перезагрузился...#restart\n\n@RudeusNG @FremanMQ')
    while True:
        await bot.send_message(chat_id='-1001592098459', text='Сервер активен...')
        await asyncio.sleep(120)
keep_alive()
if __name__ == '__main__':
    on_start = asyncio.get_event_loop()
    on_start.create_task(on())
    asyncio.run(aiogram.executor.start_polling(dp, skip_updates=True))
    loop = asyncio.get_event_loop()
    loop.create_task(perform_update_income())
    executor.start_polling(dp, skip_updates=True)