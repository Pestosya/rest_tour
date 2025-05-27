from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_inline_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Подобрать тур", callback_data="pick_tour")],
        # [InlineKeyboardButton(text="🏨 Забронировать отель", callback_data="book_hotel")],
        [InlineKeyboardButton(text="📞 Связаться с агентом", url="https://t.me/doncigars")]
    ])

def confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"),
            InlineKeyboardButton(text="✏️ Изменить", callback_data="edit")
        ]
    ])

def confirm_keyboard_hotel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_hotel"),
            InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_hotel")
        ]
    ])

def choose_edit_field():
    builder = InlineKeyboardBuilder()
    builder.button(text="🌍 Страна", callback_data="edit_country")
    builder.button(text="🌙 Ночей", callback_data="edit_nights")
    builder.button(text="📅 Дата вылета", callback_data="edit_approx_date")
    builder.button(text="👥 Кол-во человек", callback_data="edit_people")
    builder.button(text="💰 Бюджет", callback_data="edit_budget")
    builder.button(text="📝 Комментарий", callback_data="edit_comment")
    builder.adjust(2)
    return builder.as_markup()


def choose_country_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇹🇷 Турция", callback_data="country_Турция")
    builder.button(text="🇪🇬 Египет", callback_data="country_Египет")
    builder.button(text="🇦🇪 ОАЭ", callback_data="country_ОАЭ")
    builder.button(text="🇹🇭 Таиланд", callback_data="country_Таиланд")
    builder.button(text="🇬🇷 Греция", callback_data="country_Греция")
    builder.button(text="🇮🇹 Италия", callback_data="country_Италия")
    builder.adjust(2)
    return builder.as_markup()

def choose_date_from_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 5-7", callback_data="nights_5")
    builder.button(text="📅 10-12", callback_data="nights_10")
    builder.button(text="📅 13-14", callback_data="nights_13")
    builder.button(text="📝 Указать вручную", callback_data="nights_manual")
    builder.adjust(2,1,1)
    return builder.as_markup()

def choose_people_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="1", callback_data="people_1")
    builder.button(text="2", callback_data="people_2")
    builder.button(text="3", callback_data="people_3")
    builder.button(text="4+", callback_data="people_4plus")
    builder.adjust(2)
    return builder.as_markup()

def choose_budget_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="💰 100–150к", callback_data="budget_<50")
    builder.button(text="💰 150-200к", callback_data="budget_50-100")
    builder.button(text="💰 250–300к", callback_data="budget_100-150")
    builder.button(text="💰 300к+", callback_data="budget_150+")
    builder.adjust(2)
    return builder.as_markup()
