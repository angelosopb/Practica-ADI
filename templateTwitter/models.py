#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-

from flask import jsonify
from google.appengine.ext import ndb

class Operacion(ndb.Model):
    tipo = ndb.StringProperty(required=True)
    usuario = ndb.StringProperty(required=True)
    dato = ndb.StringProperty(required=True)
    fecha = ndb.DateTimeProperty(auto_now_add=True)
    
    @property
    def toJSON(self):
        aux = {
            'id':self.key.id(),
            'tipo':self.tipo,
            'usuario':self.usuario,
	    'dato':self.dato,
            'fecha':self.fecha,}
        return aux
