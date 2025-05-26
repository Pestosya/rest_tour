from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from config import ADMIN_IDS
from states import TourRequest, TourRequestHotel
from keyboards import (
    main_inline_menu, confirm_keyboard, confirm_keyboard_hotel,
    choose_edit_field
)
from utils.csv_export import write_tour, write_hotel, TOUR_FILE, HOTEL_FILE
from broadcast import send_broadcast

router = Router()

# /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.full_name

    users_file = Path("data/users.csv")
    users_file.parent.mkdir(parents=True, exist_ok=True)
    if users_file.exists():
        with open(users_file, "r", encoding="utf-8") as f:
            if user_id in f.read():
                pass
            else:
                with open(users_file, "a", encoding="utf-8") as f_append:
                    f_append.write(f"{user_id},{user_name}\n")
    else:
        with open(users_file, "w", encoding="utf-8") as f:
            f.write("id,name\n")
            f.write(f"{user_id},{user_name}\n")

    await message.answer(
        "👋 Привет! Я помогу тебе подобрать тур или забронировать отель.\n\nВыбери действие:",
        reply_markup=main_inline_menu()
    )


# --- PICK TOUR ---
@router.callback_query(F.data == "pick_tour")
async def inline_pick_tour(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🌍 В какую страну планируете поездку?")
    await state.set_state(TourRequest.country)

@router.message(TourRequest.country)
async def pick_date_from(message: Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer("📅 Дата начала поездки?")
    await state.set_state(TourRequest.date_from)

@router.message(TourRequest.date_from)
async def pick_date_to(message: Message, state: FSMContext):
    await state.update_data(date_from=message.text)
    await message.answer("📅 Дата окончания поездки?")
    await state.set_state(TourRequest.date_to)

@router.message(TourRequest.date_to)
async def pick_people(message: Message, state: FSMContext):
    await state.update_data(date_to=message.text)
    await message.answer("👥 Сколько человек?")
    await state.set_state(TourRequest.people)

@router.message(TourRequest.people)
async def pick_budget(message: Message, state: FSMContext):
    await state.update_data(people=message.text)
    await message.answer("💰 Какой у вас бюджет?")
    await state.set_state(TourRequest.budget)

@router.message(TourRequest.budget)
async def pick_comment(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer("📝 Пожелания? (если нет — напишите 'нет')")
    await state.set_state(TourRequest.comment)

import re

PHONE_REGEX = re.compile(r"^\\+?[789]\\d{9,14}$")

@router.message(TourRequest.comment)
async def ask_phone(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await message.answer(
        "📞 ✍️ Пожалуйста, отправьте ваш номер телефона и подтвердите согласие на обработку персональных данных.\n\n"
        "Пример: +79991234567"
    )
    await state.set_state(TourRequest.phone)

import re

PHONE_REGEX = re.compile(r"^\+?\d{10,15}$")

@router.message(TourRequest.phone)
async def pick_confirm(message: Message, state: FSMContext):
    phone = message.text.strip()

    if not PHONE_REGEX.match(phone):
        await message.answer("❌ Пожалуйста, введите номер телефона корректно. Пример: +79991234567")
        return

    await state.update_data(phone=phone)
    data = await state.get_data()

    text = (
        "📩 <b>Проверьте данные заявки</b>\n"
        f"🌍 Страна: {data['country']}\n"
        f"📅 Даты: {data['date_from']} — {data['date_to']}\n"
        f"👥 Людей: {data['people']}\n"
        f"💰 Бюджет: {data['budget']}\n"
        f"📝 Комментарий: {data['comment']}\n"
        f"📞 Телефон: {data['phone']}\n\n"
        "Вы всё ввели верно?"
    )
    await message.answer(text, reply_markup=confirm_keyboard())

@router.callback_query(F.data == "confirm")
async def submit_tour(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = (
        "📩 <b>Заявка на подбор тура</b>\n"
        f"🌍 Страна: {data['country']}\n"
        f"📅 Даты: {data['date_from']} — {data['date_to']}\n"
        f"👥 Людей: {data['people']}\n"
        f"💰 Бюджет: {data['budget']}\n"
        f"📝 Комментарий: {data['comment']}\n"
        f"📞 Телефон: {data['phone']}\n\n"
        f"👤 От: {callback.from_user.full_name} (ID: {callback.from_user.id})"
    )
    for admin_id in ADMIN_IDS:
        await callback.bot.send_message(admin_id, text)
    write_tour(data, callback.from_user)
    await callback.message.edit_text("✅ Заявка отправлена!", reply_markup=main_inline_menu())
    await state.clear()

@router.callback_query(F.data == "edit")
async def edit_tour(callback: CallbackQuery):
    await callback.message.edit_text("✏️ Что вы хотите изменить?", reply_markup=choose_edit_field())

# --- HOTEL BOOKING ---
@router.callback_query(F.data == "book_hotel")
async def inline_book_hotel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🏨 В каком городе/стране хотите забронировать отель?")
    await state.set_state(TourRequestHotel.city)

@router.message(TourRequestHotel.city)
async def hotel_date_from(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("📅 Дата заезда?")
    await state.set_state(TourRequestHotel.date_from)

@router.message(TourRequestHotel.date_from)
async def hotel_date_to(message: Message, state: FSMContext):
    await state.update_data(date_from=message.text)
    await message.answer("📅 Дата выезда?")
    await state.set_state(TourRequestHotel.date_to)

@router.message(TourRequestHotel.date_to)
async def hotel_stars(message: Message, state: FSMContext):
    await state.update_data(date_to=message.text)
    await message.answer("⭐️ Категория отеля (например, 3*, 4*)?")
    await state.set_state(TourRequestHotel.stars)

@router.message(TourRequestHotel.stars)
async def hotel_comment(message: Message, state: FSMContext):
    await state.update_data(stars=message.text)
    await message.answer("📝 Пожелания? (если нет — напишите 'нет')")
    await state.set_state(TourRequestHotel.comment)

@router.message(TourRequestHotel.comment)
async def hotel_confirm(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    text = (
        "🏨 <b>Проверьте данные бронирования</b>\n"
        f"📍 Город: {data['city']}\n"
        f"📅 Даты: {data['date_from']} — {data['date_to']}\n"
        f"⭐️ Категория: {data['stars']}\n"
        f"📝 Комментарий: {data['comment']}\n\n"
        "Вы всё ввели верно?"
    )
    await message.answer(text, reply_markup=confirm_keyboard_hotel())

@router.callback_query(F.data == "confirm_hotel")
async def submit_hotel(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = (
        "🏨 <b>Заявка на бронирование отеля</b>\n"
        f"📍 Город: {data['city']}\n"
        f"📅 Даты: {data['date_from']} — {data['date_to']}\n"
        f"⭐️ Категория: {data['stars']}\n"
        f"📝 Комментарий: {data['comment']}\n"
        f"👤 От: {callback.from_user.full_name} (ID: {callback.from_user.id})"
    )
    for admin_id in ADMIN_IDS:
        await callback.bot.send_message(admin_id, text)
    write_hotel(data, callback.from_user)
    await callback.message.edit_text("✅ Заявка отправлена!", reply_markup=main_inline_menu())
    await state.clear()

@router.callback_query(F.data == "edit_hotel")
async def edit_hotel(callback: CallbackQuery):
    await callback.message.edit_text("✏️ Что вы хотите изменить?", reply_markup=choose_edit_field(is_tour=False))

# --- EDIT TOUR FIELDS ---
@router.callback_query(F.data == "edit_country")
async def edit_country(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🌍 Введите новую страну:")
    await state.set_state(TourRequest.country)

@router.callback_query(F.data == "edit_date_from")
async def edit_date_from(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📅 Введите новую дату начала поездки:")
    await state.set_state(TourRequest.date_from)

@router.callback_query(F.data == "edit_date_to")
async def edit_date_to(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📅 Введите новую дату окончания поездки:")
    await state.set_state(TourRequest.date_to)

@router.callback_query(F.data == "edit_people")
async def edit_people(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("👥 Введите новое количество человек:")
    await state.set_state(TourRequest.people)

@router.callback_query(F.data == "edit_budget")
async def edit_budget(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("💰 Введите новый бюджет:")
    await state.set_state(TourRequest.budget)

@router.callback_query(F.data == "edit_comment")
async def edit_comment(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝 Введите новый комментарий:")
    await state.set_state(TourRequest.comment)

# --- EDIT HOTEL FIELDS ---
@router.callback_query(F.data == "edit_city")
async def edit_city(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📍 Введите новый город:")
    await state.set_state(TourRequestHotel.city)

@router.callback_query(F.data == "edit_date_from_h")
async def edit_date_from_h(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📅 Введите новую дату заезда:")
    await state.set_state(TourRequestHotel.date_from)

@router.callback_query(F.data == "edit_date_to_h")
async def edit_date_to_h(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📅 Введите новую дату выезда:")
    await state.set_state(TourRequestHotel.date_to)

@router.callback_query(F.data == "edit_stars")
async def edit_stars(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("⭐️ Введите новую категорию отеля:")
    await state.set_state(TourRequestHotel.stars)

@router.callback_query(F.data == "edit_comment_h")
async def edit_comment_h(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝 Введите новый комментарий:")
    await state.set_state(TourRequestHotel.comment)

# --- EXPORT ---
@router.message(Command("export"))
async def export_csv(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("❌ У вас нет доступа.")

    files = []
    if TOUR_FILE.exists():
        files.append(FSInputFile(TOUR_FILE, filename="tours.csv"))
    if HOTEL_FILE.exists():
        files.append(FSInputFile(HOTEL_FILE, filename="hotels.csv"))

    if not files:
        await message.answer("❌ Пока нет заявок.")
        return

    await message.answer("📦 Вот текущие заявки:")
    for f in files:
        await message.answer_document(f)

@router.message(Command("send_broadcast"))
async def cmd_send_broadcast(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("❌ У вас нет доступа.")
    await send_broadcast()
    await message.answer("📢 Рассылка отправлена.")