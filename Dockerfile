FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
  python3.11 \
  python3-pip \
  git

COPY requirements.txt /requirements.txt

RUN pip3 install -r /requirements.txt

COPY broken_link_checker.py /usr/bin/broken_link_checker.py

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]