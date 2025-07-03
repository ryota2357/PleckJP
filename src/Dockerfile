FROM python:3.13 AS develop

RUN apt-get update     &&\
    apt-get upgrade -y &&\
    apt-get install -y \
      build-essential pkg-config gettext cmake ninja-build git locales \
      libbrotli-dev    \
      libcairo2-dev    \
      libfreetype-dev  \
      libgif-dev       \
      libgtk-3-dev     \
      libgtkmm-3.0-dev \
      libjpeg-dev      \
      libpango1.0-dev  \
      libpng-dev       \
      libreadline-dev  \
      libspiro-dev     \
      libtiff5-dev     \
      libtool          \
      libwoff-dev      \
      libxml2-dev    &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/*

# Set locale and timezone
RUN locale-gen ja_JP.UTF-8 &&\
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG=ja_JP.UTF-8  \
    LANGUAGE=ja_JP:en \
    LC_ALL=ja_JP.UTF-8
RUN ln -fs /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# Install fontforge
RUN git clone https://github.com/fontforge/fontforge --depth 1 &&\
    cd fontforge &&\
    mkdir build  &&\
    cd build     &&\
    cmake \
      -DCMAKE_BUILD_TYPE=Release   \
      -DENABLE_FONTFORGE_EXTRAS=ON \
      -GNinja ..  &&\
    ninja         &&\
    ninja install &&\
    ninja clean

# Add python module
RUN pip install --upgrade --no-cache-dir 'pip>=25.1.1' &&\
    pip install --no-cache-dir 'numpy>=2.3.1' 'fonttools>=4.58.4'

# To detect docker environment (ENV din't work, I don't know why)
RUN touch /.pleckjp-docker-inside


FROM develop AS release

RUN mkdir -p /home/pleckjp

COPY ../README.md /home/pleckjp
COPY ../LICENSE   /home/pleckjp
COPY ../Makefile  /home/pleckjp/Makefile
COPY ../src       /home/pleckjp/src
COPY ../resources /home/pleckjp/resources

WORKDIR /home/pleckjp

CMD /bin/bash
