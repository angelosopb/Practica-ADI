#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-

import os, subprocess, signal
from google.appengine.ext import ndb
from google.appengine.api import memcache
from models import Operacion
import json
from datetime import datetime
from time import gmtime, strftime
from flask import Flask, request, redirect, url_for, g, session, flash, render_template
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.config['DEBUG'] = True
memcache.add('palabra',value=0)
memcache.add('idioma',value=0)
memcache.add('likes',value=0)
memcache.add('personas',value=0)
captura = 0
capturando = False
first = 0
noper=0
app.secret_key = 'development'

oauth = OAuth()

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
    twe = []
    tweets = []
    if g.user is not None:
        resp = twitter.request('statuses/home_timeline.json')
        if resp.status == 200:
            twe = list(resp.data)
            for i in twe:
                tweets.append(str(i['id'])+" - "+g.user['screen_name']+" : "+i['text'])
        else:
            flash('Imposible cargar tweets desde Twitter')

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
    flash('Sesion cerrada')
    return redirect(url_for('index'))

#Almacenar Memcache
def storeM(tipo):
    entity = memcache.get(tipo)
    memcache.replace(tipo,value=entity+1)

#Almacenar DataStore
def storeD(tipo,dato,usuario):
    global noper
    noper += 1
    newOpe = Operacion(id=noper,tipo=tipo,usuario=usuario,dato=dato)
    newOpe.put()

# Callback
@app.route('/oauthorized')
def oauthorized():
    print(twitter)
    resp = twitter.authorized_response()
    if resp is None:
        flash('Peticion de inicio de sesion denegada')
    else:
        flash('Autentificado')
        session['twitter_oauth'] = resp
    return redirect(url_for('index'))

# Operaciones
@app.route('/op1', methods=['POST'])
def idioma():
  if first==1 and capturando==False:
    datos = True
    if g.user is None:
       return redirect(url_for('login'))

    idioma = request.form['tweetIdioma']

    if len(idioma)!=0:
       if idioma == 'español':
          print("español")
       elif idioma == 'ingles':
          print("ingles")
       elif idioma == 'ninguno':
          datos=False

    if datos == False:
       flash("No ha seleccionado ninguna de las opciones")
    else:
       storeD('idioma',idioma,g.user['screen_name'])
       storeM('idioma')
       flash('Busqueda por idioma: "%s", realizada' % idioma)

    return redirect(url_for('index'))

  else:
    flash("Debes realizar una captura y detencion antes de realizar una operacion")
    return redirect(url_for('index'))


@app.route('/op2', methods=['POST'])
def palabra():
  if first==1 and capturando==False:
    datos = True
    if g.user is None:
       return redirect(url_for('login'))

    palabra = request.form['tweetPalabra']

    if len(palabra)!=0:
       print("palabra")
    else:
       datos=False

    if datos == False:
       flash("No ha introducido nada")
    else:
       storeD("palabra",palabra,g.user['screen_name'])
       storeM("palabra")
       flash('Busqueda por la palabra "%s", realizada' % palabra)

    return redirect(url_for('index'))

  else:
    flash("Debes realizar una captura y detencion antes de realizar una operacion")
    return redirect(url_for('index'))

@app.route('/op3', methods=['POST'])
def like():
  if first==1 and capturando==False:
    datos = True
    if g.user is None:
       return redirect(url_for('login'))

    like = request.form['tweetLike']
    
    if len(like)!=0:
       print("likes")
    else:
      datos = False

    if datos == False:
       flash("No ha introducido nada")
    elif int(like)<0:
       flash("Error. No se aceptan negativos en la busqueda por likes")
    else:
       storeD("likes",like,g.user['screen_name'])
       storeM("likes")
       flash('Busqueda por likes "%s", realizada' % like)

    return redirect(url_for('index'))
    
  else:
    flash("Debes realizar una captura y detencion antes de realizar una operacion")
    return redirect(url_for('index'))
    
@app.route('/op4', methods=['POST'])
def personas():
  if first==1 and capturando==False:
    datos = True
    if g.user is None:
       return redirect(url_for('login'))

    personas = request.form['tweetPersonas']

    if len(personas)!=0:
       personas2=personas.split(";")
       print(personas2)
    else:
      datos = False

    if datos == False:
       flash("No ha introducido nada")
    else:
       storeD("personas",personas,g.user['screen_name'])
       storeM("personas")
       flash('Busqueda por personas "%s", realizada' % personas)

    return redirect(url_for('index'))

  else:
    flash("Debes realizar una captura y detencion antes de realizar una operacion")
    return redirect(url_for('index'))

@app.route('/operaciones', methods=['POST'])
def opeFechas():
  if first==1 and capturando==False:
    datos = True
    if g.user is None:
       return redirect(url_for('login'))

    operaciones = []
    formato_fecha = "%d-%m-%Y"
    finicial = request.form['fecha1']
    ffinal = request.form['fecha2']

    if len(finicial)!=0 and len(ffinal)!=0:

       finicial = datetime.strptime(finicial,formato_fecha)
       ffinal = datetime.strptime(ffinal,formato_fecha)
       op = Operacion.query(Operacion.usuario == g.user['screen_name'])

       for i in op:
         fecha, hora = str(i.fecha).split(" ")
         a, mes, dia = fecha.split("-")
         fecha = datetime.strptime(dia+"-"+mes+"-"+a,formato_fecha)
         if fecha>=finicial and fecha<=ffinal:
            operaciones.append("Busqueda por: "+i.tipo+", con dato: "+i.dato+". Realizado por: "+i.usuario+", a fecha: "+str(i.fecha))
       return render_template('index.html', operaciones=operaciones)

    else:
       datos = False

    if datos == False:
       flash("Tiene que introducir dos fechas")
       return redirect(url_for('index'))

  else:
    flash("Debes realizar una captura y detencion antes de realizar una operacion")
    return redirect(url_for('index'))

@app.route('/allop', methods=['POST'])
def operaciones():
  if first==1 and capturando==False:
    if g.user is None:
       return redirect(url_for('login'))

    operaciones = []
    op = Operacion.query(Operacion.usuario == g.user['screen_name'])

    for i in op:
         operaciones.append("Busqueda por: "+i.tipo+", con dato: "+i.dato+". Realizado por: "+i.usuario+", a fecha: "+str(i.fecha))
         f=str(i.fecha)
         fec = f.split(" ")
         print(fec)
    return render_template('index.html', operaciones=operaciones)

  else:
    flash("Debes realizar una captura y detencion antes de realizar una operacion")
    return redirect(url_for('index'))

@app.route('/captura', methods=['POST'])
def flume():
     global capturando
     global first
     first = 1
     if not capturando:
         if g.user is None:
            return redirect(url_for('login'))
         else:
            capturando = True
            cmd = "flume-ng agent -n TwitterAgent -f /home/angel/ADI/flume-1.7.0/conf/twitter.conf.template"
            global captura
            captura = subprocess.Popen(cmd, shell=True).pid
            print (str(captura))
            flash('Capturando tweets')
	    return redirect(url_for('index'))
     else:
         flash('Error. Ya estaba capturando')
         return redirect(url_for('index'))

@app.route('/parada', methods=['POST'])
def noflume():
     global capturando
     if capturando:
         if g.user is None:
            return redirect(url_for('login'))
         else:
            capturando = False
            os.kill(captura+1, signal.SIGTERM)
            flash('Parada de captura de tweets')
	    return redirect(url_for('index'))
     else:
         flash('Error. Ya estaba parado')
         return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
