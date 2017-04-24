FROM bsaifullin/testenv:latest

EXPOSE 8888

COPY docker/etc/kisschat.yml /etc/kisschat.yml 

# RUN git clone https://github.com/Kami11/chat.git

# Use local copy
ADD ./ /chat/

WORKDIR "/chat"

RUN ./setup.py install

CMD ["/bin/bash","-c", "kisschat -a 0.0.0.0"]

