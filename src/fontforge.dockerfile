FROM ubuntu:24.10

RUN apt-get update && apt-get install -y \
    build-essential gettext cmake ninja-build git ccache python3-dev python3-pip locales \
    libcairo2-dev \
    libfreetype6-dev \
    libgif-dev \
    libgtk-3-dev \
    libjpeg-dev \
    libpango1.0-dev \
    libpng-dev \
    libpython3-dev \
    libspiro-dev \
    libtiff5-dev \
    libtool \
    libxml2-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set time zoon
RUN ln -fs /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# Set locale
RUN locale-gen ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:en
ENV LC_ALL ja_JP.UTF-8

# Set python3
RUN ln -s /usr/bin/python3 /usr/bin/python
ENV PYTHON=python3

# Install fontforge
RUN git clone https://github.com/fontforge/fontforge
RUN cd fontforge     && \
    mkdir build      && \
    cd build         && \
    cmake -GNinja .. && \
    ninja            && \
    ninja install    && \
    ninja clean

# Add python module
ENV PYTHONPATH=/usr/local/lib/python3/dist-packages/
RUN pip install --upgrade --no-cache-dir 'pip>=24.3.1' &&\
    pip install --no-cache-dir --break-system-packages 'numpy>=2.1.3'
