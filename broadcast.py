from aiogram import Bot
from config import BOT_TOKEN
from pathlib import Path

BROADCAST_FILE = Path("admin_panel/data/broadcast.txt")
USERS_FILE = Path("admin_panel/data/users.csv")

async def send_broadcast():
    if not BROADCAST_FILE.exists():
        return

    lines = BROADCAST_FILE.read_text(encoding="utf-8").strip().split("\n")
    if len(lines) < 3:
        return

    date_line = lines[0]
    title = lines[1]
    message = lines[2]
    image_url = lines[3] if len(lines) > 3 and lines[3].strip() else None

    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")

    if USERS_FILE.exists():
        with open(USERS_FILE, encoding="utf-8") as f:
            next(f)  # Пропускаем заголовок
            for line in f:
                user_id = line.strip().split(",")[0]
                try:
                    text = f"<b>{title}</b>\n\n{message}"
                    if image_url:
                        await bot.send_photo(chat_id=user_id, photo=image_url, caption=text)
                    else:
                        await bot.send_message(chat_id=user_id, text=text)
                except Exception as e:
                    print(f"❌ Ошибка при отправке {user_id}: {e}")

    BROADCAST_FILE.write_text("")  # Очищаем файл после отправки
    await bot.session.close()
