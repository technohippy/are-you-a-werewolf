import cgi
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class Game(db.Model):
  wave_id = db.StringProperty()

class Participant(db.Model):
  participant_id = db.StringProperty()
  role = db.StringProperty(default='villager')
  alive = db.BooleanProperty(default=True)

