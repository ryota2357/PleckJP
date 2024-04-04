FROM python:3

RUN apt-get update && \
    apt-get install -y locales && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set time zoon
RUN ln -fs /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# Set locale
RUN locale-gen ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:en
ENV LC_ALL ja_JP.UTF-8

# Add python module
RUN pip install --upgrade --no-cache-dir 'pip>=24.0.0' && \
    pip install --no-cache-dir 'fonttools>=4.50.0'
