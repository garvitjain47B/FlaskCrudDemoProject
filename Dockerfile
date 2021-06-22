FROM python:3.8-slim-buster

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000

CMD [ "python", "./app.py", "runserver", "0.0.0.0:5000" ]

