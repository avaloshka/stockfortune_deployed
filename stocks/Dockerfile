FROM ubuntu
WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y install python3 python3-dev python3-pip \

	&& apt-get -y install python3-venv python3-wheel mysql-client

COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
