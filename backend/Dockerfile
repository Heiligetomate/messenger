FROM python:3.10-slim

WORKDIR /app

COPY .. /app

COPY requirements.txt /app/
#RUN apt update -y
#RUN apt install libpq-dev -y
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pydapper[psycopg2]
RUN pip install websockets

#EXPOSE 6789

ENV PYTHONUNBUFFERED=1

CMD ["python", "./src/main.py"]
