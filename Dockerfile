FROM python:3.5

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
        libatlas-base-dev gfortran supervisor

COPY ./requirements.txt /project/requirements.txt

RUN pip3 install -r /project/requirements.txt

COPY server-conf/supervisord.conf /etc/supervisor/

COPY src /project/src

WORKDIR /project

CMD ["/usr/bin/supervisord"]
