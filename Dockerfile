FROM ubuntu:22.10

ENV DEBIAN_FRONTEND=noninteractive

# https://github.com/fontforge/fontforge/blob/master/INSTALL.md
RUN apt update && \
    apt upgrade -y && \
    apt install -y build-essential gettext git cmake ninja-build python3-dev \
                   libjpeg-dev libtiff5-dev libpng-dev libfreetype6-dev libgif-dev libgtk-3-dev libxml2-dev libpango1.0-dev libcairo2-dev libspiro-dev
RUN git clone https://github.com/fontforge/fontforge
RUN cd fontforge     && \
    mkdir build      && \
    cd build         && \
    cmake -GNinja .. && \
    ninja            && \
    ninja install

# python tool
RUN apt install -y python3-fontforge
