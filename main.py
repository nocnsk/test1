import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# --- Настройки ---
BOT_TOKEN = "8349697695:AAGUybFJS22Khob4V0-Ir1KCJ6vdWEbOsY4"  # ← замените на свой

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

class BioAgeStates(StatesGroup):
    gender = State()
    age = State()
    height = State()
    waist = State()
    hips = State()
    weight = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Я помогу рассчитать ваш биологический возраст по методике Горелкина и Пинхасова.\n\n"
        "Выберите ваш пол:",
        reply_markup=[
            [{"text": "Женщина"}],
            [{"text": "Мужчина"}]
        ]
    )
    await state.set_state(BioAgeStates.gender)

@router.message(BioAgeStates.gender, F.text.in_(["Женщина", "Мужчина"]))
async def process_gender(message: Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await message.answer("Введите ваш возраст в годах (с точностью до 0.1, например: 45.3):")
    await state.set_state(BioAgeStates.age)

@router.message(BioAgeStates.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = float(message.text.replace(',', '.'))
        if age <= 0:
            raise ValueError
        await state.update_data(age=age)
        await message.answer("Введите ваш рост в метрах (с точностью до 0.005, например: 1.75):")
        await state.set_state(BioAgeStates.height)
    except:
        await message.answer("Пожалуйста, введите корректный возраст (число, например: 45.3):")

@router.message(BioAgeStates.height)
async def process_height(message: Message, state: FSMContext):
    try:
        height = float(message.text.replace(',', '.'))
        if height <= 0:
            raise ValueError
        await state.update_data(height=height)
        await message.answer("Окружность талии в см (с точностью до 0.5, например: 84.0):")
        await state.set_state(BioAgeStates.waist)
    except:
        await message.answer("Пожалуйста, введите корректный рост (число, например: 1.75):")

@router.message(BioAgeStates.waist)
async def process_waist(message: Message, state: FSMContext):
    try:
        waist = float(message.text.replace(',', '.'))
        if waist <= 0:
            raise ValueError
        await state.update_data(waist=waist)
        await message.answer("Окружность бёдер в см (например: 96.5):")
        await state.set_state(BioAgeStates.hips)
    except:
        await message.answer("Пожалуйста, введите корректную окружность талии (число, например: 84.0):")

@router.message(BioAgeStates.hips)
async def process_hips(message: Message, state: FSMContext):
    try:
        hips = float(message.text.replace(',', '.'))
        if hips <= 0:
            raise ValueError
        await state.update_data(hips=hips)
        await message.answer("Вес в кг (например: 70.2):")
        await state.set_state(BioAgeStates.weight)
    except:
        await message.answer("Пожалуйста, введите корректную окружность бёдер (число, например: 96.5):")

@router.message(BioAgeStates.weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.replace(',', '.'))
        if weight <= 0:
            raise ValueError
        await state.update_data(weight=weight)
    except:
        await message.answer("Пожалуйста, введите корректный вес (число, например: 70.2):")
        return
    data = await state.get_data()
    gender = data["gender"]
    age = data["age"]
    height = data["height"]
    waist = data["waist"]
    hips = data["hips"]
    weight = data["weight"]

    # Расчёт
    try:
        if gender == "Женщина":
            optimal_age = 18.0
            rl = age - optimal_age
            if rl <= 0:
                await message.answer("Методика применима только для женщин старше 18 лет.")
                return
            denominator = hips * (height ** 2) * (14.7 + 0.26 * rl + 0.01 * rl)
            kss = (waist * weight) / denominator
            bio_age = kss * rl + 18.0
        else:  # Мужчина
            optimal_age = 21.0
            rl = age - optimal_age
            if rl <= 0:
                await message.answer("Методика применима только для мужчин старше 21 года.")
                return
            denominator = hips * (height ** 2) * (17.2 + 0.31 * rl + 0.0012 * rl)
            kss = (waist * weight) / denominator
            bio_age = kss * rl + 21.0

        bio_age = round(bio_age, 1)
        await message.answer(f"Ваш биологический возраст: {bio_age} лет")
    except ZeroDivisionError:
        await message.answer("Ошибка: деление на ноль. Проверьте введённые данные (особенно рост и объёмы).")
    except Exception as e:
        await message.answer(f"Произошла ошибка при расчёте: {str(e)}")

    await state.clear()

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
