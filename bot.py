import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '7682618151:AAGPkcLsux6vNUH33KcX1K-J9z5zgoJPlEk'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# In-memory storage for users
users = {}
matches = {}

class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_goal = State()

@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer("Привет! 🎯 Я бот для знакомств ко Дню Святого Валентина. Как тебя зовут?")
    await Registration.waiting_for_name.set()

@dp.message_handler(state=Registration.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await Registration.waiting_for_age.set()

@dp.message_handler(state=Registration.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, укажи возраст числом.")
        return
    await state.update_data(age=int(message.text))
    await message.answer("Какова твоя цель? 💕 Для романтики или 🤝 Для партнерства? (ответь 'романтика' или 'партнерство')")
    await Registration.waiting_for_goal.set()

@dp.message_handler(state=Registration.waiting_for_goal)
async def process_goal(message: types.Message, state: FSMContext):
    goal = message.text.lower()
    if goal not in ['романтика', 'партнерство']:
        await message.answer("Пожалуйста, выбери: 'романтика' или 'партнерство'.")
        return
    user_data = await state.get_data()
    users[message.from_user.id] = {
        'name': user_data['name'],
        'age': user_data['age'],
        'goal': goal
    }
    await state.finish()
    await message.answer("Отлично! Я подберу для тебя пару. 🔍")
    await match_user(message)

async def match_user(message: types.Message):
    user_id = message.from_user.id
    for other_id, other_data in users.items():
        if other_id != user_id and other_data['goal'] == users[user_id]['goal'] and other_id not in matches.values():
            matches[user_id] = other_id
            matches[other_id] = user_id

            await bot.send_message(user_id, f"🎯 Ваша пара: {other_data['name']}, {other_data['age']} лет!")
            await bot.send_message(other_id, f"🎯 Ваша пара: {users[user_id]['name']}, {users[user_id]['age']} лет!")
            return
    await message.answer("Пока нет подходящей пары. Я сообщу, как только кто-то появится! ⏳")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
