from flask import Flask, jsonify, request, render_template, render_template_string, Markup, make_response
from routes.v1 import app, cache, db, Logger
import requests, uuid
# import sys
# sys.setrecursionlimit(10000)
from datetime import datetime, timedelta
from database.tenders import Category, Tender, Bid, Document
from .extensionHelpers import Extenstion
from werkzeug.utils import secure_filename

import boto3, botocore
import boto, os
from boto.s3.key import Key
from botocore.client import Config

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/tenders")
@cache.cached(timeout=app.config['CACHE_DURATION'])
def tenders():
	Logger(request.method, request.endpoint, request.url, 'Listing all tenders', request.headers.get('User-Agent'), request.accept_languages)
	tenders = Tender.query.filter(Tender.application_close_date > datetime.now()).all()
	data = []
	for tender in tenders:
		response = {}
		response['public_id'] = tender.public_id
		response['owner_id'] = tender.owner_id
		response['created_at'] = Extenstion.convertDate(tender.created_at)
		response['category_id'] = tender.category_id
		response['title'] = tender.title
		response['description'] = tender.description
		response['application_start_date'] = Extenstion.convertDate(tender.application_start_date)
		response['application_close_date'] = Extenstion.convertDate(tender.application_close_date)
		response['category'] = Extenstion.getCategoryName(tender.category_id)
		response['docs'] = Extenstion.getTenderDocuments(tender.public_id)
		response['num_of_bids'] = Bid.query.filter_by(tender_id=tender.public_id).count()
		data.append(response)
	
	db.session.close()

	responseObject = {
		'data' : data,
		'len' : len(tenders)
	}
	return jsonify(responseObject), 200


@app.route('/create/tender', methods=['POST'])
def createTender():
	category_id = request.json.get('category_id')
	type_id = request.json.get('type_id')
	owner_id = request.json.get('owner_id')
	title = request.json.get('title')
	description = request.json['description']
	application_start_date = request.json.get('application_start_date')
	application_close_date = request.json.get('application_close_date')

	new_tender = Tender(
		public_id = str(uuid.uuid4()),
		category_id = category_id,
		type_id = type_id,
		owner_id = owner_id,
		title = title,
		description = description,
		application_start_date = application_start_date,
		application_close_date = application_close_date,
		created_at = datetime.now()
	)

	Tender.save_to_db(new_tender)
	responseObject = { "message"  : "Successfully saved added the tender" } 
	return jsonify(responseObject), 200

@app.route('/tenders/<public_id>')
def getTender(public_id):
	tender = Tender.query.filter_by(public_id=public_id).first()

	if not tender:
		responseObject = {
			'message' : 'No such tender can be found'
		}
		return jsonify(responseObject), 412

	bids = []
	bid_data = Bid.query.filter_by(tender_id=public_id).all()
	for bid in bid_data:
		response = {}
		response['supplier_id'] = bid.supplier_id
		response['amount'] = int(bid.amount)
		response['supplier'] = Extenstion.getUserName(bid.supplier_id)
		response['duration'] = bid.duration
		response['applied_at'] = Extenstion.convertDate(bid.created_at)
		response['public_id'] = bid.public_id
		response['docs'] = Extenstion.getBidDocuments(bid.public_id)
		bids.append(response)

	responseObject = {
			'public_id' : tender.public_id,
			'category_id' : tender.category_id,
			'title' : tender.title,
			'description' : tender.description,
			'application_start_date' : Extenstion.convertDate(tender.application_start_date),
			'application_close_date' : Extenstion.convertDate(tender.application_close_date),
			'category' :  Extenstion.getCategoryName(tender.category_id),
			'created_at' : Extenstion.convertDate(tender.created_at),
			'owner_id' : tender.owner_id,
			'bids' : bids,
			'docs' : Extenstion.getTenderDocuments(tender.public_id)
	}
	return jsonify(responseObject), 200

@app.route('/tender/doc/upload/<public_id>', methods=['POST'])
def upload_tender_file(public_id):
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			responseObject = {'message': 'No file part'}
			return make_response(jsonify(responseObject)), 200
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			responseObject = {'message': 'No file Selected'}
			return make_response(jsonify(responseObject)), 200
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			path = app.config['UPLOAD_FOLDER'] + filename
			try:
				ACCESS_KEY_ID = app.config['S3_ACCESS_KEY']
				ACCESS_SECRET_KEY = app.config['S3_SECRET_KEY']
				BUCKET_NAME = app.config['S3_BUCKET']
				FILE_NAME = path

				data = open(FILE_NAME, 'rb')

				# S3 Connect
				s3 = boto3.resource(
					's3',
					aws_access_key_id=ACCESS_KEY_ID,
					aws_secret_access_key=ACCESS_SECRET_KEY,
					config=Config(signature_version='s3v4')
				)

				# Image Uploaded
				s3.Bucket(BUCKET_NAME).put_object(Key=FILE_NAME, Body=data, ACL='public-read')

				tender = db.session.query(Tender).filter_by(public_id=public_id).first_or_404()

				if not tender:
					responseObject = {
						'message' : 'Tender does not exist'
					}
					return make_response(jsonify(responseObject)), app.config['ERROR_CODE']

				new_doc = Document(
					public_id = str(uuid.uuid4()),
					created_at = datetime.now(),
					tender_id = public_id,
					doc_url = 'https://s3.eu-west-2.amazonaws.com/{0}/docs/{1}'.format(app.config['S3_BUCKET'], filename),
					doc_type = 'XYZ'
				)
				Document.save_to_db(new_doc)
				responseObject = {
					'message' : 'Successfully uploaded'
				}
				return make_response(jsonify(responseObject)), 200
			except Exception as identifier:
				responseObject = {
					'error' : str(identifier),
					'message' : 'Could not upload image to remote server'
				}
				return make_response(jsonify(responseObject)), 500