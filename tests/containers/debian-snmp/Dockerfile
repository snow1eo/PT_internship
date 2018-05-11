FROM debian:stretch
MAINTAINER Max Melnikov <mmelnikov@ptsecurity.com>

RUN groupadd -r snmpsim && useradd --no-log-init -r -g snmpsim snmpsim 

RUN apt update && apt-get -y install openssh-server --no-install-recommends &&  apt -y install python3-pip supervisor && pip3 install snmpsim

COPY public.snmprec* /opt/
COPY show /sbin/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /var/run/snmpsim/ && mkdir -p /var/run/sshd && chown -R snmpsim:snmpsim /var/run/snmpsim/ /opt/ && chmod 777 /sbin/show
RUN echo "root:pwd" | chpasswd
RUN sed -i "s/#PermitRootLogin prohibit-password/PermitRootLogin yes/" /etc/ssh/sshd_config && ln -s /sbin/show /sbin/sh

# SSH login fix. Otherwise user is kicked off after login
RUN sed "s@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g" -i /etc/pam.d/sshd 

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22 161/udp

CMD ["/usr/bin/supervisord"]

