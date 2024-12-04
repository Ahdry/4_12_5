from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

API_TOKEN = ''

# Создание объекта бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Определение состояний
class Form(StatesGroup):
    age = State()
    weight = State()
    height = State()
    activity_level = State()


# Главная функция, срабатывающая на команду /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_calculate = types.KeyboardButton('Рассчитать')
    button_info = types.KeyboardButton('Информация')
    keyboard.add(button_calculate, button_info)
    await message.answer("Выберите опцию:", reply_markup=keyboard)


# Функция для отображения Inline-клавиатуры
@dp.message_handler(text='Рассчитать')
async def main_menu(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    button_calories = types.InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
    button_formulas = types.InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
    keyboard.add(button_calories, button_formulas)
    await message.answer("Выберите опцию:", reply_markup=keyboard)


# Функция для обработки нажатия на кнопку 'Формулы расчёта'
@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    formula_text = "Формула Миффлина-Сан Жеора:\n" \
                   "Для мужчин: BMR = 10 * вес + 6.25 * рост - 5 * возраст + 5\n" \
                   "Для женщин: BMR = 10 * вес + 6.25 * рост - 5 * возраст - 161"
    await call.message.answer(formula_text)
    await call.answer()  # Убираем "ожидание" на кнопке


# Функция для обработки нажатия на кнопку 'Рассчитать норму калорий'
@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery):
    await Form.age.set()  # Переход в состояние ввода возраста

    await call.message.answer("Введите ваш возраст:")
    await call.answer()  # Убираем "ожидание" на кнопке


# Обработка ввода возраста
@dp.message_handler(state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    age = message.text
    await state.update_data(age=age)
    await Form.next()  # Переход к следующему состоянию
    await message.answer("Введите ваш вес (в кг):")


# Обработка ввода веса
@dp.message_handler(state=Form.weight)
async def process_weight(message: types.Message, state: FSMContext):
    weight = message.text
    await state.update_data(weight=weight)
    await Form.next()  # Переход к следующему состоянию
    await message.answer("Введите ваш рост (в см):")


# Обработка ввода роста
@dp.message_handler(state=Form.height)
async def process_height(message: types.Message, state: FSMContext):
    height = message.text
    await state.update_data(height=height)
    await Form.next()  # Переход к следующему состоянию
    await message.answer("Выберите уровень активности:\n1. Низкий\n2. Средний\n3. Высокий")

# Обработчик всех текстовых сообщений
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def all_messages(message: types.Message):
    await message.reply("Вы написали: " + message.text)


# Обработка ввода уровня активности
@dp.message_handler(state=Form.activity_level)
async def process_activity_level(message: types.Message, state: FSMContext):
    activity_level = message.text
    user_data = await state.get_data()
    age = user_data.get('age')
    weight = user_data.get('weight')
    height = user_data.get('height')

    # Здесь можно добавить логику расчёта нормы калорий на основе введённых данных
    # Например, формула расчёта норм калорий
    await message.answer(
        f"Ваши данные:\nВозраст: {age}\nВес: {weight}\nРост: {height}\nУровень активности: {activity_level}")

    await state.finish()  # Завершение состояния


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
