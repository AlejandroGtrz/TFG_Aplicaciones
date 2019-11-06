FROM python:3.7-alpine

WORKDIR /Monolito
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

EXPOSE 5000
CMD ["python3", "api.py"]
