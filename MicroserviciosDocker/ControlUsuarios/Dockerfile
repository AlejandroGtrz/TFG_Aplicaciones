FROM python:3.7-alpine

WORKDIR /Microservicios/ControlUsuarios
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /Microservicios/ControlUsuarios

CMD ["python3", "usuarios.py"]



