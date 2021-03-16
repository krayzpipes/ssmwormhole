FROM ubuntu:20.04

RUN apt-get update && apt-get install -y curl unzip openssh-client

WORKDIR /tmp

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb" \
    && dpkg -i session-manager-plugin.deb \
    && rm -rf /tmp/*

RUN adduser --gecos "" --disabled-password wormhole

COPY wormhole/ /home/wormhole/

RUN chown -R wormhole:wormhole /home/wormhole \
    && chmod 400 /home/wormhole/.ssh/WormholeKey.pem \
    && chmod 500 /home/wormhole/bin/wormhole.sh \
    && ln -s /home/wormhole/bin/wormhole.sh /usr/bin/wormhole

