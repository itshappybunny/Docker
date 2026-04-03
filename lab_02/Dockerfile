# Используем легковесный образ Python
FROM python:3.9-slim

# Устанавливаем переменную, чтобы логи Python сразу отображались в терминале
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app/script.py .

# Запуск скрипта
CMD ["python", "script.py"]