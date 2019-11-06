from flask import Flask, abort, request, jsonify, g, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import uuid
import os
from functools import wraps
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db=SQLAlchemy(app)

class CuestionarioUsuario(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    id_usuario=db.Column(db.Integer)
    id_cuestionario=db.Column(db.Integer)
    terminado=db.Column(db.Boolean)
    puntuacion=db.Column(db.Float)

class RespuestaUsuario(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    id_cuestionario_usuario=db.Column(db.Integer, db.ForeignKey('cuestionario_usuario.id'))
    id_opcion=db.Column(db.Integer)
    id_pregunta=db.Column(db.Integer)
    valor=db.Column(db.Float)

@app.route('/resolver/<cuestionario_id>', methods=['POST'])
def iniciar_cuestionario(cuestionario_id):
    token=request.headers['x-access-token']
    x=requests.get(url='http://0.0.0.0:5050/verify', headers={'x-access-token': token})
    if 'id' not in x.json():
        return jsonify(x.json())
    id_usuario= x.json()['id']
    usuariocuestionario_nuevo=CuestionarioUsuario(id_usuario=id_usuario, id_cuestionario=cuestionario_id,terminado=0, puntuacion=0)
    db.session.add(usuariocuestionario_nuevo)
    db.session.flush()
    temp=requests.get(url='http://0.0.0.0:8080/cuestionario/'+cuestionario_id, json={'usuariocuestionario': usuariocuestionario_nuevo.id})
    db.session.commit()
    return jsonify(temp.json())
@app.route('/opcion', methods=['POST'])
def responder_opcion():
    data=request.get_json()
    token=request.headers['x-access-token']
    x=requests.get(url='http://0.0.0.0:5050/verify', headers={'x-access-token': token})
    if 'id' not in x.json():
        return jsonify(x.json())
    id_usuario= x.json()['id']
    texto_opcion=data['opcion']
    id_usuariocuestionario=data['id_usuariocuestionario']
    texto_pregunta=data['pregunta']
    usuariocuestionario=CuestionarioUsuario.query.get_or_404(id_usuariocuestionario)
    if id_usuario!=usuariocuestionario.id_usuario:
        return {"Mensaje": "Error, usuario no autorizado para resolver"}
    ##Le pido al servicio que controla los cuestionarios la pregunta
    peticion_pregunta=requests.get(url='http://0.0.0.0:8080/pregunta', json={'texto':texto_pregunta,'id_cuestionario':usuariocuestionario.id_cuestionario})
    id_pregunta=peticion_pregunta.json()['id_pregunta']
    ##Le pido al servicio que controla los cuestionarios la opcion
    peticion_opcion=requests.get(url='http://0.0.0.0:8080/opcion', json={'texto':texto_opcion,'id_pregunta':id_pregunta})
    id_opcion=peticion_opcion.json()['id_opcion']
    valor=peticion_opcion.json()['valor']
    if RespuestaUsuario.query.filter(RespuestaUsuario.id_cuestionario_usuario==id_usuariocuestionario).filter(RespuestaUsuario.id_pregunta==id_pregunta).first() is not None:
        return jsonify({'Mensaje': 'Pregunta ya contestada'})
    nueva_respuesta=RespuestaUsuario(id_pregunta=id_pregunta,id_opcion=id_opcion,id_cuestionario_usuario=id_usuariocuestionario, valor=valor)
    usuariocuestionario.puntuacion=usuariocuestionario.puntuacion+valor
    msg=''
    db.session.flush()
    if valor<=0:
        msg='Incorrecta'
    else:
        msg='Correcta'
    db.session.add(nueva_respuesta)
    db.session.flush()
    numero_respuestas=RespuestaUsuario.query.filter(RespuestaUsuario.id_cuestionario_usuario==usuariocuestionario.id).count()
    ##Le pido el numero de preguntas que tiene el cuestionario
    peticion_numero_preguntas=requests.get(url='http://0.0.0.0:8080/numero_preguntas/'+str(usuariocuestionario.id_cuestionario))
    numero_preguntas=peticion_numero_preguntas.json()['numero_preguntas']
    if numero_respuestas==numero_preguntas:
        usuariocuestionario.terminado=1
    db.session.commit()
    return jsonify({'Resultado': msg})
@app.route('/cuestionario/resultados', methods=['GET'])
def obtener_resultados():
    token=request.headers['x-access-token']
    x=requests.get(url='http://0.0.0.0:5050/verify', headers={'x-access-token': token})
    if 'id' not in x.json():
        return jsonify(x.json())
    id_usuario= x.json()['id']
    usuario_cuestionarios=CuestionarioUsuario.query.filter(CuestionarioUsuario.id_usuario==id_usuario).filter(CuestionarioUsuario.terminado==1).all()
    lista=[]
    for u in usuario_cuestionarios:
        lista.append({'id_cuestionario': u.id_cuestionario, 'id': u.id})
    y=requests.get(url='http://0.0.0.0:8080/cuestionario/resultados', json=lista)
    return jsonify(y.json())
@app.route('/valor')
def obtener_valor():
    data= request.get_json()
    respuesta_usuario=RespuestaUsuario.query.filter(RespuestaUsuario.id_cuestionario_usuario==data['id_usuario_cuestionario']).filter(RespuestaUsuario.id_pregunta==data['id_pregunta']).first()
    return jsonify({'valor': respuesta_usuario.valor, 'opcion': respuesta_usuario.id_opcion})
@app.route('/puntuacion/<id_cuestionario_usuario>')
def obtener_puntuacion(id_cuestionario_usuario):
    cuestionario_usuario=CuestionarioUsuario.query.filter(CuestionarioUsuario.id==id_cuestionario_usuario).first()
    return jsonify({'puntuacion':cuestionario_usuario.puntuacion})
@app.route('/cuestionario_usuario', methods=['DELETE'])
def borrar_cuestionario_usuario():
    data=request.get_json()
    cuestionario_usuario=CuestionarioUsuario.query.filter(CuestionarioUsuario.id_cuestionario==data['id_cuestionario']).all()
    for c in cuestionario_usuario:
        RespuestaUsuario.query.filter(RespuestaUsuario.id_cuestionario_usuario==c.id).delete()
        db.session.delete(c)
    db.session.commit()
    return 200
if __name__== "__main__":
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(host='0.0.0.0', port=8000)
