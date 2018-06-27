FROM local/mercury-core:latest
ADD . /usr/src/mercury-agent
ADD ./mercury-agent-docker.yaml /etc/mercury/mercury-agent.yaml
RUN pip install -r /usr/src/mercury-agent/requirements.txt
RUN cd /usr/src/mercury-agent && pip install -e .

CMD mercury-agent
