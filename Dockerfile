FROM python:3.12-slim
# RUN apt-get update && apt-get upgrade -y && apt-get autoremove -y

WORKDIR /app
COPY requirements.txt ./
COPY vxtwtr.py ./
RUN pip install --no-cache-dir -r requirements.txt

# TOKEN env-var needs the discord token to run
CMD [ "python", "/app/vxtwtr.py" ]
