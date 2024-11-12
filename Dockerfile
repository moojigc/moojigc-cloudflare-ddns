FROM python:3.9

WORKDIR /home/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY *.py .
COPY check_all_zones.sh .

CMD [ "bash", "check_all_zones.sh" ]