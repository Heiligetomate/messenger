# base python image for custom image
FROM python:latest

# create working directory and install pip dependencies
WORKDIR /src
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# copy python project files from local to /hello-py image working directory
COPY . .

# run the flask server
CMD [ "python", "backend/main.py"]