FROM ubuntu:latest

ARG NODE_VERSION=24.x

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt upgrade -y && apt autoremove
RUN apt install -y python3 git rsync apt-transport-https ca-certificates curl gnupg
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /usr/share/keyrings/nodesource.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_VERSION nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
RUN echo "Package: nodejs\
Pin: origin deb.nodesource.com\
Pin-Priority: 600" | tee /etc/apt/preferences.d/nodejs
RUN apt update && apt install -y nodejs && npm i -g npm

COPY deployment.py /usr/local/bin/deployment

ENTRYPOINT ["python3", "/usr/local/bin/deployment"]
