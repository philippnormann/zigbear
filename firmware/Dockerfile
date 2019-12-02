FROM ubuntu

RUN apt-get update && \
    apt-get -y install \
    wget vim unzip \
    scons mercurial \
    python3 python3-pip \
    binutils-avr gcc-avr avr-libc \
    doxygen

RUN useradd -ms /bin/bash uracoli
USER uracoli

RUN mkdir /home/uracoli/work
WORKDIR /home/uracoli/work

RUN hg clone https://hg.savannah.nongnu.org/hgweb/uracoli/
WORKDIR /home/uracoli/work/uracoli

RUN rm Config/examples.cfg Config/packages.cfg 
COPY config/* Config/
COPY app/* Src/App/
RUN scons raspbee

COPY extract.sh .

CMD ./extract.sh
