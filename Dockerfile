FROM python
WORKDIR /
ADD . /src/mercury/agent
ADD docker/mercury-agent-docker.yaml /etc/mercury/mercury-agent.yaml
RUN pip install -r /src/mercury/agent/requirements.txt
RUN pip install -e /src/mercury/agent
RUN apt-get -y update
RUN apt-get -y install pciutils
EXPOSE 9003
EXPOSE 9004

