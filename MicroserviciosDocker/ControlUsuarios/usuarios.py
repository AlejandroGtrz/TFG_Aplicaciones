from flask import Flask, abort, request, jsonify, g, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import uuid
import os
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


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing'}), 401
        try:
            data=jwt.decode(token, app.config['SECRET_KEY'])
            current_user=User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    hashed_password= generate_password_hash(data['contrasena'], method='sha256')
    nombre=data['nombre']
    email=data['email']
    if User.query.filter_by(email = email).first() is not None:
        return jsonify({'mensaje': 'El usuario ya existe'})
    usuario_nuevo= User(public_id=str(uuid.uuid4()), nombre=nombre, email=email, contrasena=hashed_password)
    db.session.add(usuario_nuevo)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario creado'})

@app.route('/login')
def login():
    auth= request.get_json()
    email=auth['email']
    contrasena=auth['contrasena']
    user= User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Usuario no encontrado"})
    if check_password_hash(user.contrasena, contrasena):
        token=jwt.encode({'public_id': user.public_id,'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token.decode('UTF-8')})
    return jsonify({'token': "Error"})
    
@app.route('/verify')
@token_required
def verify(current_user):
    dict={'id': current_user.id}
    return jsonify(dict)

if __name__== "__main__":
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(host='0.0.0.0', port=5050)
