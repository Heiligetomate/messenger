FROM ubuntu:latest
LABEL authors="heili"

ENTRYPOINT ["top", "-b"]