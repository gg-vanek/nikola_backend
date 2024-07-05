FROM python:3.12

LABEL maintainer="vanek"
LABEL t="backend"

# Задаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем переменные окружения, чтобы убедиться, что Python выходит на stdout и stderr
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=off DISPLAY_UPDATE_PROMPT=no

# Копируем зависимости
COPY requirements.txt /app/

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем остальные файлы проекта в контейнер
COPY . /app/

RUN chmod +x ./backend_entrypoint.sh
RUN chmod +x ./celery_entrypoint.sh
RUN chmod +x ./flower_entrypoint.sh
