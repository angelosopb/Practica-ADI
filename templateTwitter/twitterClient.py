#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-


from time import gmtime, strftime
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

    return render_template('index.html', tweets=tweets)

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

#Se cogen los tweets con flume luego con pig se filtra por el idioma y se devuelven a la api la tweets filtrados y se muestran
    datos = True
    if g.user is None:
       return redirect(url_for('login'))

    idioma = request.form['tweetIdioma']

    if len(idioma)!=0:
       response = twitter.post('statuses/destroy/'+id_eliminar+'.json')
    else:
       datos = False

    if datos == False:
       flash("No ha introducido datos")
    else:
       if response.status == 403:
          flash("Error: #%d, %s " % (
              response.data.get('errors')[0].get('code'),
              response.data.get('errors')[0].get('message'))
          )
       elif response.status == 401:
            flash('Error de autentificacion con Twitter.')
       else:
            flash('Búsqueda por idioma "#%s" realizada' % idioma)

    return redirect(url_for('index'))



@app.route('/op2', methods=['POST'])
def palabra():
    datos = True
    if g.user is None:
       return redirect(url_for('login'))

    palabra = request.form['tweetPalabra']

    if len(palabra)!=0:
       response = twitter.post('statuses/retweet/'+id_retweet+'.json')
    else:
       datos=False

    if datos == False:
       flash("No ha introducido datos")
    else:
       if response.status == 403:
           flash("Error: #%d, %s " % (
               response.data.get('errors')[0].get('code'),
               response.data.get('errors')[0].get('message'))
           )
       elif response.status == 401:
           flash('Error de autentificacion con Twitter.')
       else:
           flash('Búsqueda por palabra "#%s" realizada' % palabra)

    return redirect(url_for('index'))


@app.route('/op3', methods=['POST'])
def like():
    datos = True
    if g.user is None:
       return redirect(url_for('login'))

    like = request.form['tweetLike']
    
    if len(like)!=0:
       response = twitter.post('friendships/create.json?screen_name='+id_name+'&follow=true')
    else:
      datos = False

    if datos == False:
       flash("No ha introducido nada")
    else:
       if response.status == 403:
          flash("Error: #%d, %s " % (
               response.data.get('errors')[0].get('code'),
               response.data.get('errors')[0].get('message'))
          )
       elif response.status == 401:
            flash('Error de autentificacion con Twitter.')
       else:
            flash('Búsqueda por likes "#%s" realizada' % like)

    return redirect(url_for('index'))
    

    
@app.route('/op4', methods=['POST'])
def personas():
    if g.user is None:
       return redirect(url_for('login'))

    personas = request.form['tweetPersonas']

    response = twitter.post('statuses/update.json', data={'status': texto})

    if response.status == 403:
        flash("Error: #%d, %s " % (
            response.data.get('errors')[0].get('code'),
            response.data.get('errors')[0].get('message'))
        )
    elif response.status == 401:
        flash('Error de autentificacion con Twitter.')
    else:
        flash('Búsqueda por personas "#%s" realizada' % personas)

    return redirect(url_for('index'))

@app.route('/', methods=['POST'])
def opeFechas():
    datos = True    
    op = []
    operaciones = []

    if g.user is not None:
        finicial = request.form['fecha1']
    	ffinal = request.form['fecha2']
    
    	if id_name:
    	   response = twitter.post('friendships/create.json?screen_name='+id_name+'&follow=true')
    	elif id_user:
           response = twitter.post('friendships/create.json?user_id='+id_user+'&follow=true')
    	else:
      	   datos = False
    	if datos == False:
       	   flash("Solo debe introducir uno o no ha introducido nada")
    	else:
       	   if response.status == 403:
          	flash("Error: #%d, %s " % (
               		response.data.get('errors')[0].get('code'),
               		response.data.get('errors')[0].get('message'))
          	)
       	   elif response.status == 401:
           	 flash('Error de autentificacion con Twitter.')
       	   else:
            	flash('Siguiendo a #%s (ID: #%s)' % (response.data['name'],response.data['id']))
           
           resp = twitter.request('statuses/home_timeline.json')
           if resp.status == 200:
            op = list(resp.data)
            for i in op:
                operaciones.append(str(i['id'])+" - "+g.user['screen_name']+" : "+i['text'])
           else:
            flash('Imposible cargar tweets desde Twitter')
    else:
	return redirect(url_for('login'))

    return render_template('index.html', operaciones=operaciones)

@app.route('/', methods=['POST'])
def operaciones():
    op = []
    operaciones = []
    if g.user is not None:
        resp = twitter.request('statuses/home_timeline.json')
        if resp.status == 200:
            op = list(resp.data)
            for i in op:
                operaciones.append(str(i['id'])+" - "+g.user['screen_name']+" : "+i['text'])
        else:
            flash('Imposible cargar tweets desde Twitter')
    else:
	return redirect(url_for('login'))

    return render_template('index.html', operaciones=operaciones)

if __name__ == '__main__':
    app.run()
