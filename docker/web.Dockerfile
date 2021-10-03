# syntax=docker/dockerfile:1
FROM ubuntu:20.04
RUN apt update && apt install -y --no-install-recommends python3 python3-venv build-essential python3-dev openssl libssl-dev
ENV VIRTUAL_ENV=/opt/s2db-venv
RUN python3 -m venv $VIRTUAL_ENV
RUN mkdir -p /var/s2db/uploads
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY requirements-web.txt .
RUN pip install -r requirements-web.txt
COPY s2db /opt/s2db
EXPOSE 5000
RUN openssl genrsa -out dummy.key 4096 && openssl req -new -key dummy.key -out dummy.csr -subj "/CN=\${domain}/C=XX/L= /O= " && openssl x509 -req -days 365 -in dummy.csr -signkey dummy.key -out dummy.crt
RUN chmod uog+r dummy.key
CMD uwsgi --https :5000,dummy.crt,dummy.key --wsgi-file /opt/s2db/web/app.py --callable app --processes 4 --threads 2
#CMD uwsgi --http :5000 --wsgi-file /opt/s2db/web/app.py --callable app --processes 4 --threads 2
