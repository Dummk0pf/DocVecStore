# syntax=docker/dockerfile:1.5

FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y software-properties-common wget && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3.11-dev && \
    apt install poppler-utils -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONBUFFERED 1

RUN mkdir vector_search

WORKDIR /vector_search

COPY ./src/settings/requirements.txt requirements.txt

RUN python3.11 -m venv .venv && . .venv/bin/activate && pip install -r ./requirements.txt