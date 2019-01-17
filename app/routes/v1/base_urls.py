from flask import Flask, jsonify, request, render_template, render_template_string
from routes.v1 import app, cache, db, Logger
import requests, uuid
from datetime import datetime, timedelta, date
from database.tenders import Category, Type, Tender, Bid, BidDocument
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
		response['num_of_tenders'] = Extenstion.getTenderCount(category.public_id)
		response['status'] = 'Active' if category.status == 5 else 'In Active'
		output.append(response)
	return jsonify(output), 200

@app.route("/category/<public_id>")
def categoryTenders(public_id):
	Logger(request.method, request.endpoint, request.url, 'Fetching tenders under categoty {}'.format(public_id), request.headers.get('User-Agent'), request.accept_languages)
	tenders = Tender.query.filter_by(category_id=public_id).all()

	if not tenders:
		return jsonify({'message' :'No tenders under that category'}), 412
	
	data = []
	for tender in tenders:
		response = {}
		response['public_id'] = tender.public_id
		response['owner_id'] = tender.owner_id
		response['company_name'] = Extenstion.getCompanyName(tender.owner_id)
		response['created_at'] = Extenstion.convertDate(tender.created_at)
		response['category_id'] = tender.category_id
		response['title'] = tender.title.upper()
		response['tender_code'] = tender.tender_code
		response['status'] = 'Active' if tender.status == 5 else 'Awarded'
		response['description'] = tender.description
		response['application_start_date'] = Extenstion.convertDate(tender.application_start_date)
		response['application_close_date'] = Extenstion.convertDate(tender.application_close_date)
		response['category'] = Extenstion.getCategoryName(tender.category_id)
		response['docs'] = Extenstion.getTenderDocuments(tender.public_id)
		response['num_of_bids'] = Bid.query.filter_by(tender_id=tender.public_id).count()
		data.append(response)
	db.session.close()
	return jsonify(data), 200


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

@app.route('/post/categories', methods=['POST'])
def AddCategory():
	name = request.json['name']
	description = request.json['description']

	is_category = Category.query.filter_by(name=name).first()

	if is_category:
		return jsonify({'message' : 'Cannot add that category'}), 422
	
	new_category = Category(
		public_id = str(uuid.uuid4()),
		name= name,
		description = description,
		created_at = datetime.now()
	)
	new_category.save_to_db()
	return jsonify({'message' : 'Succesfully saved the new category'}), 200

@app.route('/type/categories', methods=['POST'])
def AddType():
	name = request.json['name']
	description = request.json['description']

	is_category = Type.query.filter_by(name=name).first()

	if is_category:
		return jsonify({'message' : 'Cannot add that type'}), 422
	
	new_category = Category(
		public_id = str(uuid.uuid4()),
		name= name,
		description = description,
		created_at = datetime.now()
	)
	new_category.save_to_db()
	return jsonify({'message' : 'Succesfully saved the new category'}), 200


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