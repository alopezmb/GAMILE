FROM python:3.9-slim-bullseye

COPY requirements.txt /.
RUN pip3 install -r /requirements.txt

WORKDIR /mesa/

CMD ["python", "run.py"]