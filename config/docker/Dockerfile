FROM python:3.12

LABEL maintainer="vanek"
LABEL t="backend"

WORKDIR /app/backend
COPY ../.. .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod +x ./config/scripts/entrypoint.sh
ENTRYPOINT ["/bin/bash", "./config/scripts/entrypoint.sh"]
