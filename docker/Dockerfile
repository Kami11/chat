FROM bsaifullin/testenv:latest

RUN git clone https://github.com/Kami11/chat.git

WORKDIR "/chat"

RUN ./setup.py install

CMD ["/bin/bash","-c", "kisschat -a 0.0.0.0"]

