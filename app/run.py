from flask import Flask, jsonify, render_template, url_for, request, redirect, json
from flask_sqlalchemy import SQLAlchemy, functools
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta

import pymysql, os, math, requests, uuid

import cherrypy
from cherrypy import log

import logging
from logging.handlers import *
import logging.config

# Directory imports
from routes.v1 import app, logger


if __name__ == '__main__':
	LOG_CONF = {
		'version': 1,
		'formatters': {
			'void': {
				'format': ''
			},
			'standard': {
				'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
			},
		},
		'handlers': {
			'default': {
				'level':'INFO',
				'class':'logging.StreamHandler',
				'formatter': 'standard',
				'stream': 'ext://sys.stdout'
			},
			'cherrypy_console': {
				'level':'INFO',
				'class':'logging.StreamHandler',
				'formatter': 'void',
				'stream': 'ext://sys.stdout'
			},
			'cherrypy_access': {
				'level':'INFO',
				'class': 'logging.handlers.RotatingFileHandler',
				'formatter': 'void',
				'filename': 'app.log',
				'maxBytes': 10485760,
				'backupCount': 20,
				'encoding': 'utf8'
			},
			'cherrypy_error': {
				'level':'INFO',
				'class': 'logging.handlers.RotatingFileHandler',
				'formatter': 'void',
				'filename': 'app.log',
				'maxBytes': 10485760,
				'backupCount': 20,
				'encoding': 'utf8'
			},
		},
		'loggers': {
			'': {
				'handlers': ['default'],
				'level': 'INFO'
			},
			'db': {
				'handlers': ['default'],
				'level': 'INFO' ,
				'propagate': False
			},
			'cherrypy.access': {
				'handlers': ['cherrypy_access'],
				'level': 'INFO',
				'propagate': False
			},
			'cherrypy.error': {
				'handlers': ['cherrypy_console', 'cherrypy_error'],
				'level': 'INFO',
				'propagate': False
			},
		}
}
	# app_logged = TransLogger(app)
	# Mount the application
	cherrypy.tree.graft(app, "/")
	cherrypy.config.update({
		'global' : {
			'engine.autoreload.on' : True,
			'log.screen': True
		},
		'log.screen': True,
		'log.error_file': "app.log"
	})
	# Unsubscribe the default server
	cherrypy.server.unsubscribe()

	# Instantiate a new server object
	server = cherrypy._cpserver.Server()

	# Configure the server object
	server.socket_host = "0.0.0.0"
	server.socket_port = 5000
	server.thread_pool = 100
	server.log = True
	server.screen = True

	# For SSL Support
	# server.ssl_module            = 'pyopenssl'
	# server.ssl_certificate       = 'ssl/certificate.crt'
	# server.ssl_private_key       = 'ssl/private.key'
	# server.ssl_certificate_chain = 'ssl/bundle.crt'

	# Subscribe this server
	server.subscribe()

	# Start the server engine (Option 1 *and* 2)
	logging.config.dictConfig(LOG_CONF)
	cherrypy.engine.start()
	cherrypy.engine.block()
