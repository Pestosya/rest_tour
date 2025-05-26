from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from broadcast import send_broadcast
from config import ADMIN_IDS
from states import TourRequest, TourRequestHotel
from keyboards import (
    main_inline_menu, confirm_keyboard, confirm_keyboard_hotel,
    choose_edit_field
)
from utils.csv_export import write_tour, write_hotel, TOUR_FILE, HOTEL_FILE


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.full_name

    users_file = Path("data/users.csv")
    users_file.parent.mkdir(parents=True, exist_ok=True)
    if users_file.exists():
        with open(users_file, "r", encoding="utf-8") as f:
            if user_id not in f.read():
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
    msg = await callback.message.answer("🌍 В какую страну планируете поездку?")
    await state.set_state(TourRequest.country)
    await state.update_data(ui_msg_id=msg.message_id)

@router.message(TourRequest.country)
async def pick_date_from(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(country=message.text)
    msg_id = (await state.get_data()).get("ui_msg_id")
    await message.bot.edit_message_text("📅 Дата начала поездки?", message.chat.id, msg_id)
    await state.set_state(TourRequest.date_from)

@router.message(TourRequest.date_from)
async def pick_date_to(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(date_from=message.text)
    msg_id = (await state.get_data()).get("ui_msg_id")
    await message.bot.edit_message_text("📅 Дата окончания поездки?", message.chat.id, msg_id)
    await state.set_state(TourRequest.date_to)

@router.message(TourRequest.date_to)
async def pick_people(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(date_to=message.text)
    msg_id = (await state.get_data()).get("ui_msg_id")
    await message.bot.edit_message_text("👥 Сколько человек поедет?", message.chat.id, msg_id)
    await state.set_state(TourRequest.people)

@router.message(TourRequest.people)
async def pick_budget(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(people=message.text)
    msg_id = (await state.get_data()).get("ui_msg_id")
    await message.bot.edit_message_text("💰 Какой у вас бюджет?", message.chat.id, msg_id)
    await state.set_state(TourRequest.budget)

@router.message(TourRequest.budget)
async def pick_comment(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(budget=message.text)
    msg_id = (await state.get_data()).get("ui_msg_id")
    await message.bot.edit_message_text("📝 Есть ли пожелания? (если нет — напишите 'нет')", message.chat.id, msg_id)
    await state.set_state(TourRequest.comment)

@router.message(TourRequest.comment)
async def pick_confirm(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(comment=message.text)
    data = await state.get_data()
    msg_id = data["ui_msg_id"]
    text = (
        "📩 <b>Проверьте данные заявки</b>\n"
        f"🌍 Страна: {data['country']}\n"
        f"📅 Даты: {data['date_from']} — {data['date_to']}\n"
        f"👥 Людей: {data['people']}\n"
        f"💰 Бюджет: {data['budget']}\n"
        f"📝 Комментарий: {data['comment']}\n"
        "Вы всё ввели верно?"
    )
    await message.bot.edit_message_text(text, message.chat.id, msg_id, reply_markup=confirm_keyboard())

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
        f"👤 От: {callback.from_user.full_name} (ID: {callback.from_user.id})\n"
    )
    for admin_id in ADMIN_IDS:
        await callback.bot.send_message(admin_id, text)
    write_tour(data, callback.from_user)
    await callback.message.edit_text("✅ Заявка отправлена!", reply_markup=main_inline_menu())
    await state.clear()

# --- HOTEL BOOKING ---
@router.callback_query(F.data == "book_hotel")
async def inline_book_hotel(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.answer("🏨 В каком городе/стране хотите забронировать отель?")
    await state.set_state(TourRequestHotel.city)
    await state.update_data(ui_msg_id=msg.message_id)

@router.message(TourRequestHotel.city)
async def hotel_date_from(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(city=message.text)
    msg_id = (await state.get_data()).get("ui_msg_id")
    await message.bot.edit_message_text("📅 Дата заезда?", message.chat.id, msg_id)
    await state.set_state(TourRequestHotel.date_from)

@router.message(TourRequestHotel.date_from)
async def hotel_date_to(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(date_from=message.text)
    msg_id = (await state.get_data()).get("ui_msg_id")
    await message.bot.edit_message_text("📅 Дата выезда?", message.chat.id, msg_id)
    await state.set_state(TourRequestHotel.date_to)

@router.message(TourRequestHotel.date_to)
async def hotel_stars(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(date_to=message.text)
    msg_id = (await state.get_data()).get("ui_msg_id")
    await message.bot.edit_message_text("⭐️ Категория отеля (например, 3*, 4*)?", message.chat.id, msg_id)
    await state.set_state(TourRequestHotel.stars)

@router.message(TourRequestHotel.stars)
async def hotel_comment(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(stars=message.text)
    msg_id = (await state.get_data()).get("ui_msg_id")
    await message.bot.edit_message_text("📝 Есть ли пожелания? (если нет — напишите 'нет')", message.chat.id, msg_id)
    await state.set_state(TourRequestHotel.comment)

@router.message(TourRequestHotel.comment)
async def hotel_confirm(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(comment=message.text)
    data = await state.get_data()
    msg_id = data["ui_msg_id"]
    text = (
        "🏨 <b>Проверьте данные бронирования</b>\n"
        f"📍 Город: {data['city']}\n"
        f"📅 Даты: {data['date_from']} — {data['date_to']}\n"
        f"⭐️ Категория: {data['stars']}\n"
        f"📝 Комментарий: {data['comment']}\n"
        "Вы всё ввели верно?"
    )
    await message.bot.edit_message_text(text, message.chat.id, msg_id, reply_markup=confirm_keyboard_hotel())

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


@router.callback_query(F.data == "confirm_hotel")
async def submit_hotel(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = (
        "🏨 <b>Заявка на бронирование отеля</b>\n"
        f"📍 Город: {data['city']}\n"
        f"📅 Даты: {data['date_from']} — {data['date_to']}\n"
        f"⭐️ Категория: {data['stars']}\n"
        f"📝 Комментарий: {data['comment']}\n"
        f"👤 От: {callback.from_user.full_name} (ID: {callback.from_user.id})\n"
    )
    for admin_id in ADMIN_IDS:
        await callback.bot.send_message(admin_id, text)
    write_hotel(data, callback.from_user)
    await callback.message.edit_text("✅ Заявка отправлена!", reply_markup=main_inline_menu())
    await state.clear()

# --- EXPORT ---
@router.message(Command("export"))
async def export_csv(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("❌ У вас нет доступа.")
    files = []
    if TOUR_FILE.exists():
        files.append(FSInputFile(TOUR_FILE, filename="../../Downloads/tours.csv"))
    if HOTEL_FILE.exists():
        files.append(FSInputFile(HOTEL_FILE, filename="hotels.csv"))
    if not files:
        await message.answer("❌ Пока нет заявок.")
        return
    await message.answer("📦 Вот текущие заявки:")
    for f in files:
        await message.answer_document(f)

# --- SEND BROADCAST ---
@router.message(Command("send_broadcast"))
async def cmd_send_broadcast(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("❌ У вас нет доступа.")
    await send_broadcast()
    await message.answer("📢 Рассылка отправлена.")
