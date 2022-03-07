# syntax=docker/dockerfile:1

FROM python:3
WORKDIR /df
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN pip3 install -e .
CMD ["peak-management"]