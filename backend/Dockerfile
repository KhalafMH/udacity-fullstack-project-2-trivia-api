FROM python:3.7

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENV FLASK_APP=flaskr
CMD flask run
