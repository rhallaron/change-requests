FROM python:3.12.3

WORKDIR /app/

RUN apt-get update
RUN apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/rhallaron/change-requests.git .

RUN pip install -r ./requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health