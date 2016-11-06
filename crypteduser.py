#!/usr/bin/env python
# crypteduser

import jwt
from flask import Flask, request, abort, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from passlib.hash import pbkdf2_sha256
import ConfigParser
import os


def readconf():
    config = ConfigParser.ConfigParser()
    config.read(['/etc/crypteduser.conf', 'crypteduser.conf'])
    return config

app = Flask(__name__)
config = readconf()
app.debug = config.get('Main', 'debug')
app.config['SQLALCHEMY_DATABASE_URI'] = config.get('Main', 'db_uri')
db = SQLAlchemy(app)
secret_key = config.get('Main', 'secret_key')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username


def hashpass(password):
    return pbkdf2_sha256.encrypt(password)


@app.route('/adduser/', methods=['POST'])
def adduser():
    username = request.form["username"]
    password = request.form["password"]
    newuser = User(username, hashpass(password))
    try:
        db.session.add(newuser)
        db.session.commit()
    except IntegrityError:
        # user already exists
        abort(401, 'failed')
    return '%s added' % username


@app.route('/verifycookie/', methods=['GET'])
def verifycookie():
    try:
        encoded = request.cookies.get('user')
        assert encoded is not None
    except:
        abort(403, 'no cookie')
    try:
        payload = jwt.decode(encoded, secret_key, algorithms=['HS256'])
    except jwt.DecodeError:
        abort(403, 'failed decode')
    return 'ok'


@app.route('/verifyuser/', methods=['POST'])
def verifyuser():
    username = request.form["username"]
    password = request.form["password"]
    dbuser = User.query.filter_by(username=username).first()
    if dbuser is not None:
        if pbkdf2_sha256.verify(password, dbuser.password):
            # user ok, return JWT cookie
            encoded = jwt.encode({ 'uid': username }, secret_key, algorithm='HS256')
            resp = make_response('ok')
            resp.set_cookie('user', encoded)
            return resp
    abort(403, 'failed')


@app.route('/updatepass/', methods=['POST'])
def updatepass():
    username = request.form["username"]
    password = request.form["password"]
    dbuser = User.query.filter_by(username=username).first()
    if dbuser is not None:
        dbuser.password = hashpass(password)
        db.session.commit()
        return 'ok'
    abort(401, 'failed')

if __name__ == '__main__':
    if os.environ.get('CREATEDB') is not None:
        print 'creating database'
        db.create_all()
    else:
        app.run()
