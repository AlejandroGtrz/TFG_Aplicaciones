FROM python:3.7-alpine

WORKDIR /Microservicios/AccionesCuestionarios
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /Microservicios/AccionesCuestionarios

EXPOSE 8000
CMD ["python3", "operaciones.py"]



