#Dockerfile to run PEAK's Directory Facilitator agent
FROM python:3.9.6

RUN pip install peak-mas

EXPOSE 10000

CMD [ "peak", "df" ]