FROM ubuntu

RUN apt-get update && \
    apt-get -y install \
    wget vim unzip \
    python3 python3-pip \
    binutils-avr gcc-avr avr-libc

RUN useradd -ms /bin/bash uracoli
USER uracoli

RUN mkdir /home/uracoli/work
WORKDIR /home/uracoli/work

ENV uracoli_version 0.4.2

RUN wget https://download.savannah.nongnu.org/releases/uracoli/uracoli-src-${uracoli_version}.zip && \
    unzip uracoli-src-${uracoli_version}.zip && \
    rm uracoli-src-${uracoli_version}.zip

ENTRYPOINT /bin/bash
