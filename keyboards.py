from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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

def choose_edit_field(is_tour=True):
    if is_tour:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌍 Страна", callback_data="edit_country")],
            [InlineKeyboardButton(text="📅 Дата начала", callback_data="edit_date_from")],
            [InlineKeyboardButton(text="📅 Дата окончания", callback_data="edit_date_to")],
            [InlineKeyboardButton(text="👥 Кол-во человек", callback_data="edit_people")],
            [InlineKeyboardButton(text="💰 Бюджет", callback_data="edit_budget")],
            [InlineKeyboardButton(text="📝 Комментарий", callback_data="edit_comment")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📍 Город", callback_data="edit_city")],
            [InlineKeyboardButton(text="📅 Дата заезда", callback_data="edit_date_from_h")],
            [InlineKeyboardButton(text="📅 Дата выезда", callback_data="edit_date_to_h")],
            [InlineKeyboardButton(text="⭐ Категория", callback_data="edit_stars")],
            [InlineKeyboardButton(text="📝 Комментарий", callback_data="edit_comment_h")],
        ])
