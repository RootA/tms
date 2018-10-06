from flask import Flask, jsonify, request, render_template, render_template_string
from routes.v1 import app, cache, db, Logger
import requests
# import sys
# sys.setrecursionlimit(10000)

from database.tenders import Category

@app.route("/")
# @cache.cached(timeout=app.config['CACHE_DURATION'])
def index():
	Logger(request.method, request.endpoint, request.url, 'Welcome to the home page', request.headers.get('User-Agent'), request.accept_languages)
	categories = Category.query.all()
	return render_template('home.html', name=app.config['APP_NAME'], categories=categories)


@app.errorhandler(404)
def page_not_found():
	responseObject ={
		'message' : 'This is not the page you are looking for. Move along.'
	}
	return make_response(jsonify(responseObject)), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	Logger(request.method,request.endpoint, request.url, error, request.headers.get('User-Agent'), request.accept_languages)
	return jsonify({'message' : str(error)}), 500