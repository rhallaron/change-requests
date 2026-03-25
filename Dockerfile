FROM python:3.12.3

WORKDIR /app

COPY ./app /app
COPY ./requirements.txt /app/requirements.txt

RUN apt-get update
RUN apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1