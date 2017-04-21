FROM ubuntu:latest

ENV DEBIAN_FRONTEND noninteractive

ENV LANG C.UTF-8

MAINTAINER Nadezhda Troflyanina <kamikadzeim11@gmail.com>

EXPOSE 8888

COPY /etc/kisschat.yml /etc/kisschat.yml 

RUN apt-get -y update && apt-get install -y git python3 python3-pip

RUN git clone https://github.com/Kami11/chat.git

WORKDIR "/chat"

RUN ./setup.py install

CMD ["/bin/bash","-c", "kisschat -a 0.0.0.0"]

