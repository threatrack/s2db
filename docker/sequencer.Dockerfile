# syntax=docker/dockerfile:1
FROM ubuntu:20.04
RUN apt update && apt install -y --no-install-recommends python3 python3-venv radare2
ENV VIRTUAL_ENV=/opt/s2db-venv
RUN python3 -m venv $VIRTUAL_ENV
RUN mkdir -p /var/s2db/uploads
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY requirements-sequencer.txt .
RUN pip install -r requirements-sequencer.txt
COPY s2db /opt/s2db
CMD ["python3", "/opt/s2db/services/sequencer.py","-w","1"]
