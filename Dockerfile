FROM jaredrodriguez/mercury-core:0.1.4

ADD . /usr/src/mercury-api
RUN cd /usr/src/mercury-api && pip install -e .

CMD mercury-api

