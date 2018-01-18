#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-

from flask import Flask, request, redirect, url_for, g, session, flash, render_template
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.config['DEBUG'] = True
oauth = OAuth()

app.secret_key = 'development'


# FIXME: KEYs !!!!!

twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key='6dt3tPI3VWmAGvpya1oEifthI',
    consumer_secret='VPmFCfWwGI3MtRUMvWoV6chAk4h2ZyOeZjkN55vl84RJnCgRSE'
)


# Obtener token para esta sesion
@twitter.tokengetter
def get_twitter_token(token=None):
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


# Limpiar sesion anterior e incluir la nueva sesion
@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


# FIXME !!!
# Pagina principal
@app.route('/')
def index():
    if g.user is not None:
        # Ojo comprobar si hay tweets y pasarlo al html
        print "get tweets"
#        resp = twitter.request(.....
                                   
    return render_template('index.html')


# Get auth token (request)
@app.route('/login')
def login():
    callback_url=url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


# Eliminar sesion
@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


# Callback
@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('index'))




# Operaciones
@app.route('/op1', methods=['POST'])
def deleteTweet():
    return redirect(url_for('index'))



@app.route('/op2', methods=['POST'])
def retweet():
    return redirect(url_for('index'))


@app.route('/op3', methods=['POST'])
def follow():
    return redirect(url_for('index'))
    

    
@app.route('/op4', methods=['POST'])
def tweet():
    # Paso 1: Si no estoy logueado redirigir a pagina de /login
               # Usar g y redirect

    # Paso 2: Obtener los datos a enviar
               # Usar request (form)

    # Paso 3: Construir el request a enviar con los datos del paso 2
               # Utilizar alguno de los metodos de la instancia twitter (post, request, get, ...)

    # Paso 4: Comprobar que todo fue bien (no hubo errores) e informar al usuario
               # La anterior llamada devuelve el response, mirar el estado (status)

    # Paso 5: Redirigir a pagina principal (hecho)
    return redirect(url_for('index'))





if __name__ == '__main__':
    app.run()


