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
cache = Cache()
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
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']#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'
app.config['VERSION'] = 'v1'
app.config['SECRET_KEY'] = ''  # YOU MUST NEVER CHANGE THIS
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['BCRYPT_LOG_ROUNDS'] = 13  # YOU MUST NEVER CHANGE THIS
app.config['COMPANY_NAME'] = 'TMS'
app.config['APP_NAME'] = 'TMS'
app.config['MAIL_ADDRESS'] = 'accounts@tms.com'
app.config['CACHE_DURATION'] = 86400 ## Equal to a day

app.config['S3_ACCESS_KEY'] = ''
app.config['S3_SECRET_KEY'] = ''
app.config['S3_BUCKET'] = ''
app.config["S3_LOCATION"] = 'http://{0}.s3.amazonaws.com/'.format(app.config['S3_BUCKET'])
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = 'docs/'

app.config['CONFIRM_ACCOUNT_URL'] = 'http://localhost:5000/api/v1/account/confirm/{}'
app.config['SENDGRID_API_KEY'] = ''

JINJA_ENVIRONMENT.globals['STATIC_PREFIX'] = '/'

app.route = prefix_route(app.route, '/api/{0}'.format(app.config['VERSION']))

app.config['MEMCACHIER_USERNAME'] = 'B94B15'
app.config['MEMCACHIER_PASSWORD'] = '04CE925B3E939FE4A0C5A6333ED49122'
# app.config['MEMCACHIER_SERVERS'] = 'mc3.c1.eu-central-1.ec2.memcachier.com:11211'
app.config['MEMCACHIER_SERVERS'] = None
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

cache_servers = app.config['MEMCACHIER_SERVERS']
if cache_servers == None:
	# Fall back to simple in memory cache (development)
	cache.init_app(app, config={'CACHE_TYPE': 'simple'})
else:
	cache_user = app.config['MEMCACHIER_USERNAME'] or ''
	cache_pass = app.config['MEMCACHIER_PASSWORD'] or ''
	cache.init_app(app,
		config={'CACHE_TYPE': 'saslmemcached',
				'CACHE_MEMCACHED_SERVERS': cache_servers.split(','),
				'CACHE_MEMCACHED_USERNAME': cache_user,
				'CACHE_MEMCACHED_PASSWORD': cache_pass})

# cache_servers = app.config['MEMCACHIER_SERVERS']
# if cache_servers == None:
# 	cache.init_app(app, config={'CACHE_TYPE': 'simple'})
# else:
# 	cache_user = app.config['MEMCACHIER_USERNAME'] or ''
# 	cache_pass = app.config['MEMCACHIER_PASSWORD'] or ''
# 	cache.init_app(app,
# 		config=
# 			{
# 				'CACHE_TYPE': 'saslmemcached',
# 				'CACHE_MEMCACHED_SERVERS': cache_servers.split(','),
# 				'CACHE_MEMCACHED_USERNAME': cache_user,
# 				'CACHE_MEMCACHED_PASSWORD': cache_pass,
# 				'CACHE_OPTIONS': 
# 					{ 
# 						'behaviors': {
# 							# Faster IO
# 							'tcp_nodelay': True,
# 							# Keep connection alive
# 							'tcp_keepalive': True,
# 							# Timeout for set/get requests
# 							'connect_timeout': 2000, # ms
# 							'send_timeout': 750 * 1000, # us
# 							'receive_timeout': 750 * 1000, # us
# 							'_poll_timeout': 2000, # ms
# 							# Better failover
# 							'ketama': True,
# 							'remove_failed': 1,
# 							'retry_timeout': 2,
# 							'dead_timeout': 30
# 						}
# 					}
# 			}
# 		)

from routes.v1 import base_urls, oauthHelper, tenders, login, extensionHelpers, bid, signup, users


