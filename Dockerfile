FROM python:3.11.0a7-slim-bullseye

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git && apt-get install -y apt-transport-https

RUN python -m pip install "git+https://github.com/douglas/toxiproxy-python.git"
WORKDIR /usr/app/src
COPY ToxiProxyPy.py ./ToxiProxyPy.py
CMD ["python", "-u", "ToxiProxyPy.py"]
