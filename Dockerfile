FROM ubuntu:latest

USER root

RUN mkdir -p /var/lib/apt/lists/partial && chmod -R 755 /var/lib/apt/lists

RUN apt-get update && apt-get install -y \
  python3.12 \
  python3.12-venv \
  python3-pip \
  git

RUN python3.12 -m pip install --upgrade pip && \
  python3.12 -m pip install requests lxml PyYAML beautifulsoup4

COPY broken_link_checker.py /usr/bin/broken_link_checker.py

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
