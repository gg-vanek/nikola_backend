FROM python:3.11

LABEL maintainer="vanek"
LABEL t="backend"

WORKDIR /app/backend
COPY ../.. .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python manage.py wait_for_db

RUN chmod +x ./config/scripts/entrypoint.sh
ENTRYPOINT ["/bin/bash", "./config/scripts/entrypoint.sh"]
