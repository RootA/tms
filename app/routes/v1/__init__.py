from flask import Flask, jsonify, render_template, url_for, request, redirect, json, make_response
from flask_sqlalchemy import SQLAlchemy, functools
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
from babel.dates import format_date, format_datetime, format_time
import pymysql, os, math, requests, uuid, dateutil, dateutil.parser, babel

from flask_bcrypt import Bcrypt
from functools import wraps

pymysql.install_as_MySQLdb()

import cherrypy
from cherrypy import log

import logging
from logging.handlers import *
import logging.config

logger = logging.getLogger()
db_logger = logging.getLogger('db')

from flask_cache import Cache

import jinja2
JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)
	
app = Flask(__name__)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})
CORS(app)

def close(self):
	self.session.close()


def clearCache():
	#clear the cache data
	with app.app_context():
		cache.clear()

def Logger(requestType,funcName, endPoint, message, metaData, Lang):
	#Open new data file
	return cherrypy.log('requestType: [{}], timeStamp: {}, funcName : {}, api : {}, message : {}, metaData : {}, lang : {}'.format(requestType,datetime.now(), funcName, endPoint, message, metaData, Lang))

# used in route version
def prefix_route(route_function, prefix='', mask='{0}{1}'):
	def newroute(route, *args, **kwargs):
		'''New function to prefix the route'''
		return route_function(mask.format(prefix, route), *args, **kwargs)

	return newroute

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/tms'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['VERSION'] = 'v1'
app.config['SECRET_KEY'] = 'ac76697c-2cdc-4987-9de3-27e00e4dce03'  # YOU MUST NEVER CHANGE THIS
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['BCRYPT_LOG_ROUNDS'] = 13  # YOU MUST NEVER CHANGE THIS
app.config['COMPANY_NAME'] = 'TMS'
app.config['APP_NAME'] = 'TMS'
app.config['CACHE_DURATION'] = 86400 ## Equal to a day

app.config['S3_ACCESS_KEY'] = 'AKIAJTKKLLL63GRWVVEQ'
app.config['S3_SECRET_KEY'] = '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'
app.config['S3_BUCKET'] = 'olpejeta'
app.config["S3_LOCATION"] = 'http://{0}.s3.amazonaws.com/'.format(app.config['S3_BUCKET'])
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = 'docs/'

JINJA_ENVIRONMENT.globals['STATIC_PREFIX'] = '/'

app.route = prefix_route(app.route, '/api/{0}'.format(app.config['VERSION']))

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# @app.template_filter('strftime')
# def _jinja2_filter_datetime(date, fmt=None):
# 	date = dateutil.parser.parse(date)
# 	native = date.replace(tzinfo=None)
# 	format='%b %d, %Y'
# 	return native.strftime(format)

# def format_datetime(value, format='medium'):
# 	if format == 'full':
# 		format="EEEE, d. MMMM y 'at' HH:mm"
# 	elif format == 'medium':
# 		format="EE dd.MM.y HH:mm"
# 	return babel.dates.format_datetime(value, format)

# app.jinja_env.filters['datetime'] = format_datetime


# @app.template_filter('getdays')
# def _jinja2_getdays_datetime(date):
# 	date_format = "%m/%d/%Y"
# 	a = datetime.strptime(datetime.now(), date_format)
# 	b = datetime.strptime(date, date_format)
# 	delta = a - b
# 	return delta.days

from routes.v1 import base_urls, oauthHelper, tenders, login, extensionHelpers, bid