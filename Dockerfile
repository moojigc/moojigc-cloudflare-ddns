FROM python:3.9

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY *.py .

CMD [ "bash", "check_all_zones.sh" ]