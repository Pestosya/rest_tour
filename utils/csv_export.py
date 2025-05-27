import csv
from datetime import datetime
from pathlib import Path

TOUR_FILE = Path("data/tours.csv")
HOTEL_FILE = Path("data/hotels.csv")

# Убедимся, что директория существует
Path("data").mkdir(exist_ok=True)

def write_tour(data: dict, user):
    is_new = not TOUR_FILE.exists()
    with open(TOUR_FILE, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(
                ["Дата", "Имя", "Telegram ID", "Страна", "С", "По", "Человек", "Бюджет", "Комментарий", "Телефон"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            user.full_name,
            user.id,
            data["country"],
            data["approx_date"],
            data["nights"],
            data["people"],
            data["budget"],
            data["comment"],
            data["phone"]
        ])


def write_hotel(data: dict, user):
    is_new = not HOTEL_FILE.exists()
    with open(HOTEL_FILE, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["Дата", "Имя", "Telegram ID", "Город", "С", "По", "Категория", "Комментарий"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            user.full_name,
            user.id,
            data["city"],
            data["date_from"],
            data["date_to"],
            data["stars"],
            data["comment"]
        ])
