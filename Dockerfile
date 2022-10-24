FROM ubuntu:22.04


RUN apt-get -yq update && \
    apt-get install -yqq --no-install-recommends \
    git \
    wget \
    python-is-python3 \
    python3-pip

ADD requirements.txt .
RUN pip3 install -r requirements.txt
ADD scripts /scripts
RUN chmod a+x /scripts/deploy.sh

CMD ["/scripts/deploy.sh"]