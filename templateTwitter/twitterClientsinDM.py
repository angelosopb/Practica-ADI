#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-

import sys
import os, subprocess, signal
import json
import unicodedata
from datetime import datetime
from time import gmtime, strftime
from flask import Flask, request, redirect, url_for, g, session, flash, render_template
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.config['DEBUG'] = True
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

def elimina_tildes(cadena):
    s = ''.join((c for c in unicodedata.normalize('NFD',unicode(cadena)) if unicodedata.category(c) != 'Mn'))
    return s.decode()

#Leer archivo csv
def leer(archivo):
    tweets = []
    # En primer lugar debemos de abrir el fichero que vamos a leer.
    # Usa 'rb' en vez de 'r' si se trata de un fichero binario.
    infile = open(archivo, 'r')
    # Mostramos por pantalla lo que leemos desde el fichero
    print('»> Lectura del fichero línea a línea')
    for line in infile:
        tweets.append(elimina_tildes(line.decode('utf-8')))
    # Cerramos el fichero.
    infile.close()
    return tweets

# Operaciones
@app.route('/op1', methods=['POST'])
def idioma():
  if first==1 and capturando==False:
    datos = True
    tweets = []
    if g.user is None:
       return redirect(url_for('login'))

    idioma = request.form['tweetIdioma']
    print(idioma)
    if len(idioma)!=0:
       if idioma == "espanol":
          subprocess.call("pig script.py 1 es", shell=True)
          subprocess.call("hdfs dfs -copyToLocal /user/angel/out.csv /home/angel/ADI", shell=True)
          tweets = leer('/home/angel/ADI/out.csv/part-m-00000')
          print("español")
       elif idioma == "ingles":
          subprocess.call("pig script.py 1 en", shell=True)
          subprocess.call("hdfs dfs -copyToLocal /user/angel/out.csv /home/angel/ADI", shell=True)
          tweets = leer('/home/angel/ADI/out.csv/part-m-00000')
          print("ingles")
       elif idioma == 'ninguno':
          datos=False

    if datos == False:
       flash("No ha seleccionado ninguna de las opciones")
       return redirect(url_for('index'))
    else:
       print tweets
       flash('Busqueda por idioma: "%s", realizada' % idioma)
       return render_template('index.html', tweets=tweets)

  else:
    flash("Debes realizar una captura y detencion antes de realizar una operacion")
    return redirect(url_for('index'))


@app.route('/op2', methods=['POST'])
def palabra():
  if first==1 and capturando==False:
    datos = True
    tweets = []
    if g.user is None:
       return redirect(url_for('login'))

    palabra = request.form['tweetPalabra']

    if len(palabra)!=0:
          subprocess.call("pig script.py 2 "+palabra, shell=True)
          subprocess.call("hdfs dfs -copyToLocal /user/angel/out2.csv /home/angel/ADI", shell=True)
          tweets = leer('/home/angel/ADI/out2.csv/part-m-00000')
          print("palabra")
    else:
       datos=False

    if datos == False:
       flash("No ha introducido nada")
    else:
       flash('Busqueda por la palabra "%s", realizada' % palabra)
       return render_template('index.html', tweets=tweets)

  else:
    flash("Debes realizar una captura y detencion antes de realizar una operacion")
    return redirect(url_for('index'))

@app.route('/op3', methods=['POST'])
def like():
  if first==1 and capturando==False:
    datos = True
    tweets = []
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
       subprocess.call("pig script.py 3 "+like, shell=True)
       subprocess.call("hdfs dfs -copyToLocal /user/angel/out3.csv /home/angel/ADI", shell=True)
       tweets = leer('/home/angel/ADI/out3.csv/part-m-00000')
       flash('Busqueda por likes "%s", realizada' % like)
       return render_template('index.html', tweets=tweets)
    
  else:
    flash("Debes realizar una captura y detencion antes de realizar una operacion")
    return redirect(url_for('index'))
    
@app.route('/op4', methods=['POST'])
def personas():
  if first==1 and capturando==False:
    datos = True
    tweets = []
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
       flash('Busqueda por personas "%s", realizada' % personas)
       return render_template('index.html', tweets=tweets)

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
