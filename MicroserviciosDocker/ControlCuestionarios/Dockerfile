FROM python:3.7-alpine

WORKDIR /Microservicios/ControlCuestionarios
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /Microservicios/ControlCuestionarios

CMD ["python3", "cuestionarios.py"]



