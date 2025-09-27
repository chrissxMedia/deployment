FROM python:3

COPY deployment.py /usr/local/bin/deployment

CMD ["python", "/usr/local/bin/deployment"]
