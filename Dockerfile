# Файл имеет название Dockerfile
# Без расширений и с большой буквы

# Берем базовый образ с Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта (только нужное, чтобы образ был лёгким)
COPY requirements.txt .
COPY weather_bot.py .
COPY other.py .
COPY get_weather.py .
# Если есть другие файлы (handlers, config), добавь: COPY bot/ ./bot/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска бота
CMD ["python", "weather_bot.py"]
