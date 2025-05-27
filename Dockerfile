FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --upgrade pip \
 && pip install -r requirements.txt

CMD ["sh", "-c", "python bot.py & uvicorn admin_panel.main:app --host 0.0.0.0 --port 8000"]
