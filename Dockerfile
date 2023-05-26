FROM ubuntu:22.10

RUN apt-get update && apt-get install -y \
    build-essential gettext cmake ninja-build git ccache python3-dev locales \
    libtool \
    libjpeg-dev \
    libtiff5-dev \
    libpng-dev \
    libfreetype6-dev \
    libgif-dev \
    libgtk-3-dev \
    libxml2-dev \
    libpango1.0-dev \
    libcairo2-dev \
    libspiro-dev \
    libpython3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set time zoon
RUN ln -fs /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# Set locale
ENV LANG ja_JP.UTF-8
RUN locale-gen ja_JP.UTF-8
ENV LANG="ja_JP.UTF-8" \
    LANGUAGE="ja_JP:en" \
    LC_ALL="ja_JP.UTF-8"

# Set python3
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

# Add python module for fontforge
ENV PYTHONPATH=/usr/local/lib/python3/dist-packages/
