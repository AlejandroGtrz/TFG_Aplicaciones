FROM python:3.7-alpine

WORKDIR /Microservicios/Redirecciona
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /Microservicios/Redirecciona

EXPOSE 5000
CMD ["python3", "broker.py"]



