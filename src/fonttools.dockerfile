FROM python:3.13

RUN apt-get update             &&\
    apt-get upgrade -y         &&\
    apt-get install -y locales &&\
    apt-get clean              &&\
    rm -rf /var/lib/apt/lists/*

# Set locale and timezone
RUN locale-gen ja_JP.UTF-8
ENV LANG=ja_JP.UTF-8  \
    LANGUAGE=ja_JP:en \
    LC_ALL=ja_JP.UTF-8
RUN ln -fs /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# Add python module
RUN pip install --upgrade --no-cache-dir 'pip>=24.3.1' &&\
    pip install --no-cache-dir 'fonttools>=4.55.0'
