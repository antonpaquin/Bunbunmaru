FROM ubuntu:18.04
MAINTAINER Anton Paquin (docker@antonpaqu.in)

RUN apt-get update
RUN apt-get install -y \
    python3 \
    python3-pip

RUN apt-get install -y inetutils-ping

ADD requirements.txt /root/requirements.txt
RUN pip3 install -r /root/requirements.txt

ADD src /bunbunmaru

ENTRYPOINT ["/bin/bash"]
