from flask import Flask, jsonify, request, render_template, render_template_string
from routes.v1 import app, cache, db, Logger
import requests
# import sys
# sys.setrecursionlimit(10000)

from database.tenders import Category, Type
from database.users import User, Usertype
from .extensionHelpers import Extenstion


@app.route("/")
# @cache.cached(timeout=app.config['CACHE_DURATION'])
def index():
	Logger(request.method, request.endpoint, request.url, 'Welcome to the home page', request.headers.get('User-Agent'), request.accept_languages)
	categories = Category.query.all()
	if not categories:
		return []
	output = []
	for category in categories:
		response = {}
		response['name'] = category.name
		response['description'] = category.description
		response['public_id'] =  category.public_id
		response['created_at'] = Extenstion.convertDate(category.created_at)
		response['status'] = 'Active' if category.status == 5 else 'In Active'
		output.append(response)
	return jsonify(output), 200

@app.route("/types")
# @cache.cached(timeout=app.config['CACHE_DURATION'])
def indexTypes():
	categories = Type.query.all()
	if not categories:
		return []
	output = []
	for category in categories:
		response = {}
		response['name'] = category.name
		response['description'] = category.description
		response['public_id'] =  category.public_id
		response['created_at'] = Extenstion.convertDate(category.created_at)
		response['status'] = 'Active' if category.status == 5 else 'In Active'
		output.append(response)
	return jsonify(output), 200

@app.route('/usertypes')
def getUsertypes():
	usertypes = Usertype.query.filter(Usertype.name != 'Admin').all()
	if not usertypes:
		return []
	output = []
	for usertype in usertypes:
		response = {}
		response['name'] = usertype.name
		response['description'] = usertype.description
		response['public_id'] = usertype.public_id
		output.append(response)
	return jsonify(output), 200



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