
FROM python:3.10

WORKDIR /code

RUN apt-get update && apt-get install -y postgresql-client && apt-get clean

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

CMD ["/wait-for-db.sh", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]