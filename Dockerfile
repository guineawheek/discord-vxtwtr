FROM python:3.12-slim
RUN apt-get update && apt-get upgrade -y && apt-get autoremove -y

WORKDIR /app
COPY requirements.txt ./
COPY vxtwtr.py ./
RUN python -m venv ./venv
RUN ./venv/bin/pip install -U pip
RUN ./venv/bin/pip install -Ur ./requirements.txt

# TOKEN env-var needs the discord token to run
ENTRYPOINT [ "/app/venv/bin/python /app/vxtwtr.py" ]