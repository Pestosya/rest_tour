from aiogram.fsm.state import StatesGroup, State

class TourRequest(StatesGroup):
    country = State()
    date_from = State()
    date_to = State()
    people = State()
    budget = State()
    comment = State()
    phone = State ()

class TourRequestHotel(StatesGroup):
    city = State()
    date_from = State()
    date_to = State()
    stars = State()
    comment = State()
    phone = State ()
