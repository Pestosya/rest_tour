from aiogram.fsm.state import StatesGroup, State

class TourRequest(StatesGroup):
    country = State()
    nights = State()
    nights_manual = State()
    approx_date = State()
    people = State()
    budget = State()
    comment = State()
    phone = State ()
    country_edit = State()
    nights_edit = State()
    approx_date_edit = State()
    people_edit = State()
    budget_edit = State()
    comment_edit = State()
    confirmation = State()

class TourRequestHotel(StatesGroup):
    city = State()
    date_from = State()
    date_to = State()
    stars = State()
    comment = State()
    phone = State ()
