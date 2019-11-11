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
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db=SQLAlchemy(app)


class Cuestionario(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    id_creador=db.Column(db.Integer)
    titulo=db.Column(db.String(100))
    tematica=db.Column(db.String(50))
    descripcion=db.Column(db.Text())
class Pregunta(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    id_cuestionario=db.Column(db.Integer, db.ForeignKey('cuestionario.id'))
    texto=db.Column(db.String(100))
    tipo=db.Column(db.String(50))
class Opciones(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    id_pregunta=db.Column(db.Integer, db.ForeignKey('pregunta.id'))
    texto_opcion=db.Column(db.String(100))
    valor=db.Column(db.Float)
    id_cuestionario=db.Column(db.Integer, db.ForeignKey('cuestionario.id'))


@app.route('/cuestionarios', methods=['GET'])
def mostrar_cuestionarios():
    cuestionarios=Cuestionario.query
    list=[]
    for i in cuestionarios:
        list.append({'Titulo': i.titulo, 'Identificador': i.id, 'Tematica': i.tematica, 'Descripcion': i.descripcion})
    return jsonify(list)
@app.route('/cuestionarios/by_tematica/<tematica>', methods=['GET'])
def mostrar_cuestionarios_tematica(tematica):
    cuestionarios=Cuestionario.query.filter(Cuestionario.tematica.contains(tematica))
    list=[]
    for i in cuestionarios:
        list.append({'Titulo': i.titulo, 'Identificador': i.id, 'Tematica': i.tematica, 'Descripcion': i.descripcion})
    return jsonify(list)
@app.route('/cuestionarios/by_descripcion/<descripcion>', methods=['GET'])
def mostrar_cuestionarios_descripcion(descripcion):
    cuestionarios=Cuestionario.query.filter(Cuestionario.tematica.contains(descripcion))
    list=[]
    for i in cuestionarios:
        list.append({'Titulo': i.titulo, 'Identificador': i.id, 'Tematica': i.tematica, 'Descripcion': i.descripcion})
    return jsonify(list)
@app.route('/cuestionario', methods=['POST'])
def crear_cuestionario():
    data=request.get_json()
    token=request.headers['x-access-token']
    x=requests.get(url='http://usuarios:5050/verify', headers={'x-access-token': token})
    if 'id' not in x.json():
        return jsonify(x.json())
    id_usuario= x.json()['id']
    titulo=data['titulo']
    tematica=data['tematica']
    descripcion=data['descripcion']
    cuestionario_nuevo=Cuestionario(id_creador=id_usuario, titulo=titulo, tematica=tematica, descripcion=descripcion)
    db.session.add(cuestionario_nuevo)
    db.session.flush()
    preguntas=data['preguntas']
    for p in preguntas:
        print(type(p))
        print(p)
        pregunta_nueva=Pregunta(id_cuestionario=cuestionario_nuevo.id, texto=p['pregunta'], tipo=p['tipo'])
        db.session.add(pregunta_nueva)
        db.session.flush()
        opciones=p['opciones']
        solucion=p['solucion']
        n=0
        for i in opciones:
            respuesta_nueva=Opciones(id_pregunta=pregunta_nueva.id,id_cuestionario=cuestionario_nuevo.id, texto_opcion=i, valor=solucion[n])
            db.session.add(respuesta_nueva)
            n=n+1
    db.session.commit()
    return jsonify({'mensaje': 'Cuestionario creado', 'id_cuestionario': cuestionario_nuevo.id})

@app.route('/cuestionario/<id_cuestionario>', methods=['DELETE'])
def borrar_cuestionario( id_cuestionario):
    token=request.headers['x-access-token']
    x=requests.get(url='http://usuarios:5050/verify', headers={'x-access-token': token})
    if 'id' not in x.json():
        return jsonify(x.json())
    id_usuario= x.json()['id']
    cuestionario=Cuestionario.query.get_or_404(id_cuestionario)
    if(id_usuario==cuestionario.id_creador):
        db.session.delete(cuestionario)
        Opciones.query.filter(Opciones.id_cuestionario==id_cuestionario).delete()
        Pregunta.query.filter(Pregunta.id_cuestionario==id_cuestionario).delete()
        requests.delete(url='http://operaciones:8000/cuestionario_usuario', json={'id_cuestionario': id_cuestionario})
    else:
        return jsonify({'Mensaje': 'Error, solo el usuario que ha creado el cuestionario puede eliminarlo'})
    db.session.commit()
    return jsonify({'Mensaje': 'El cuestionario ha sido borrado con exito'})

@app.route('/cuestionario/<id_cuestionario>')
def obtener_cuestionario(id_cuestionario):
    cuestionario=Cuestionario.query.filter(Cuestionario.id==id_cuestionario).first()
    x={'id_usuario_cuestionario': request.get_json()['usuariocuestionario'],'titulo': cuestionario.titulo, 'preguntas': ''}
    preguntas=Pregunta.query.filter(Pregunta.id_cuestionario==cuestionario.id).all()
    list=[]
    for p in preguntas:
        opciones=Opciones.query.filter(Opciones.id_pregunta==p.id).all()
        l2=[]
        for o in opciones:
            l2.append({'id_opcion': o.id, 'opcion': o.texto_opcion })
        list.append({'id_pregunta': p.id, 'texto': p.texto, 'opciones': l2})
    x['preguntas']=list
    return jsonify(x)
@app.route('/pregunta')
def obtener_pregunta():
    data=request.get_json()
    pregunta=Pregunta.query.filter(Pregunta.id_cuestionario==data['id_cuestionario']).filter(Pregunta.texto==data['texto']).first()
    return jsonify({'id_pregunta':pregunta.id})
@app.route('/cuestionario/resultados')
def obtener_resultados():
    data = request.get_json()
    lista=[]
    for d in data:
        cuestionario=Cuestionario.query.filter(Cuestionario.id==d['id_cuestionario']).first()
        y={'usuariocuestionario':d['id'],'titulo': cuestionario.titulo, 'preguntas': "" , 'puntuacion': ''}
        preguntas=Pregunta.query.filter(Pregunta.id_cuestionario==d['id_cuestionario']).all()
        l=[]
        for p in preguntas:
            l2=[]
            opciones=Opciones.query.filter(Opciones.id_pregunta==p.id).all()
            ##Pido el valor de la respuesta
            #HASTA AQUI BIEN
            for o in opciones:
                l2.append({'opcion': o.texto_opcion})
            l.append({'pregunta': p.texto, 'opciones': l2, 'respuesta': '', 'resultado': ''})
        y['preguntas']=l
        lista.append(y)
    return jsonify(lista)
@app.route('/opcion')
def obtener_opcion():
    data=request.get_json()
    opcion=Opciones.query.filter(Opciones.id_pregunta==data['id_pregunta']).filter(Opciones.texto_opcion==data['texto']).first() 
    return jsonify({'id_opcion': opcion.id, 'valor': opcion.valor})
@app.route('/numero_preguntas/<id_cuestionario>')
def obtener_numero_preguntas(id_cuestionario):
    numero_preguntas=Pregunta.query.filter(Pregunta.id_cuestionario==id_cuestionario).count()
    return jsonify({'numero_preguntas': numero_preguntas})
if __name__== "__main__":
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(host='0.0.0.0', port=8080)
