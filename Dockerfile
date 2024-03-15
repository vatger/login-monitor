FROM python:3.11-alpine

RUN mkdir -p /opt/monitor

WORKDIR /opt/monitor

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN pip3 install waitress

COPY . .

RUN chmod +x ./init.sh

EXPOSE 8080

CMD ["/bin/sh", "-c", "./init.sh"]