from flask import Flask, abort, request, jsonify, g, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import uuid
import os
import requests
from functools import wraps

app = Flask(__name__)

@app.route('/cuestionarios', methods=['GET'])
def mostrar_cuestionarios():
    url='http://0.0.0.0:8080/cuestionarios'
    x= requests.get(url)
    return jsonify(x.json())
@app.route('/register', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    url='http://0.0.0.0:5050/register'
    x = requests.post(url, json= data)
    return jsonify(x.json())
@app.route('/login')
def login():
    data = request.get_json()
    url="http://0.0.0.0:5050/login"
    x = requests.get(url, json=data)
    return jsonify(x.json()) 
@app.route('/cuestionario', methods=['POST'])
def crear_cuestionario():
    data = request.get_json()
    url="http://0.0.0.0:8080/cuestionario"
    headers = {'x-access-token': request.headers['x-access-token']}
    x = requests.post(url, json=data, headers= headers)
    return jsonify(x.json())
@app.route('/resolver/<cuestionario_id>', methods=['POST'])
def iniciar_cuestionario(cuestionario_id):
    url="http://0.0.0.0:8000/resolver/"+cuestionario_id
    headers = {'x-access-token': request.headers['x-access-token']}
    x = requests.post(url, headers= headers)
    return jsonify(x.json())
@app.route('/cuestionario/resultados', methods=['GET'])
def obtener_resultados():
    token=request.headers['x-access-token']
    url="http://0.0.0.0:8000/cuestionario/resultados"
    x=requests.get(url, headers={'x-access-token': token})
    return jsonify(x.json())
@app.route('/cuestionario/<id_cuestionario>', methods=['DELETE'])
def borrar_cuestionario(id_cuestionario):
    url="http://0.0.0.0:8080/cuestionario/"+id_cuestionario
    headers = {'x-access-token': request.headers['x-access-token']}
    x = requests.delete(url, headers= headers)
    return jsonify(x.json())
@app.route('/opcion', methods=['POST'])
def responder_opcion():
    url="http://0.0.0.0:8000/opcion"
    data=request.get_json()
    headers = {'x-access-token': request.headers['x-access-token']}
    x = requests.post(url,json=data, headers= headers)
    return jsonify(x.json())

if __name__== "__main__":
    app.run()
