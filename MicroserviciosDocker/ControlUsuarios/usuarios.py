from flask import Flask, abort, request, jsonify, g, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import uuid
import os
import smtplib, ssl
from functools import wraps
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    public_id=db.Column(db.String(64), unique=True)
    nombre=db.Column(db.String(50))
    email=db.Column(db.String(50))
    contrasena = db.Column(db.String(64))
    activado= db.Column(db.Boolean)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'Mensaje' : 'Token is missing'}), 401
        try:
            data=jwt.decode(token, app.config['SECRET_KEY'])
            current_user=User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'Mensaje': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    hashed_password= generate_password_hash(data['contrasena'], method='sha256')
    nombre=data['nombre']
    email=data['email']
    if User.query.filter_by(email = email).first() is not None:
        return jsonify({'Mensaje': 'El usuario ya existe'})
    usuario_nuevo= User(public_id=str(uuid.uuid4()), nombre=nombre, email=email, contrasena=hashed_password)
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "alejandro.gutierrez.alv@gmail.com"  # Enter your address
    receiver_email = email  # Enter receiver address
    password = "Acman1000"
    token=jwt.encode({'public_id': usuario_nuevo.public_id}, app.config['SECRET_KEY'], algorithm='HS256')
    message="""\
    Confirmar registro


    Hola """+data['nombre']+""", por favor pulse en enlace que se encuentra a continuacion para completar el registro http://0.0.0.0:5000/verify/""" + token.decode('UTF-8')
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    db.session.add(usuario_nuevo)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario creado, revise su correo para completar el registro'})


@app.route('/login')
def login():
    auth= request.get_json()
    email=auth['email']
    contrasena=auth['contrasena']
    user= User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"Mensaje": "Usuario no encontrado"})
    if user.activado==0:
        return jsonify({"Mensaje": "El usuario no esta activado, por favor revise su correo electronico"})
    if check_password_hash(user.contrasena, contrasena):
        token=jwt.encode({'public_id': user.public_id,'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token.decode('UTF-8')})
    return jsonify({'Mensaje': "Error"})

@app.route('/usuarios', methods=['GET'])
@token_required
def usuarios(current_user):
    usuarios=User.query
    list=[]
    for u in usuarios:
        list.append({'Nombre': u.nombre})
    return jsonify(list)
@app.route('/usuarios/by_name/<nombre>', methods=['GET'])
@token_required
def usuarios_by_name(current_user, nombre):
    usuarios=User.query.filter(User.nombre.contains(nombre))
    list=[]
    for u in usuarios:
        list.append({'Nombre': u.nombre})
    return jsonify(list)

@app.route('/verify')
@token_required
def verificar(current_user):
    return jsonify({'id': current_user.id})
@app.route('/verify/<token>')
def verificar_usuario(token):
    data=jwt.decode(token, app.config['SECRET_KEY'])
    current_user=User.query.filter_by(public_id=data['public_id']).first()
    if current_user.activado==1:
        return jsonify({"Mensaje":"El usuario ya esta activado"})
    current_user.activado=1
    db.session.commit()
    return jsonify({"Mensaje":"Usuario activado con exito"})

if __name__== "__main__":
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(host='0.0.0.0', port=5050)
