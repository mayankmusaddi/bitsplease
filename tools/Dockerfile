FROM python:latest

RUN mkdir -p /bitsplease
COPY ./requirements.txt /bitsplease/requirements.txt

RUN python3 -m pip install -r /bitsplease/requirements.txt --no-cache-dir --default-timeout=1000 && pip cache purge

COPY . /bitsplease
WORKDIR /bitsplease

ENV PYTHONPATH=/bitsplease
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

EXPOSE 8501
EXPOSE 10000
