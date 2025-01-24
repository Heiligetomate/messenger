FROM python:3.10-slim

WORKDIR /app

COPY .. /app

COPY src/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install websockets

#EXPOSE 6789

ENV PYTHONUNBUFFERED=1

CMD ["python", "./src/main.py"]
