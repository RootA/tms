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
@cache.memoize()
def tenders():
	Logger(request.method, request.endpoint, request.url, 'Listing all tenders', request.headers.get('User-Agent'), request.accept_languages)
	# tenders = cache.get('all_tenders')
	# if tenders == None:
	# 	cache.set('all_tenders', tenders)
	tenders = Tender.query.filter_by(status=5).filter(Tender.application_close_date > datetime.now()).order_by(Tender.application_close_date.asc())
	data = []
	for tender in tenders:
		response = {}
		response['public_id'] = tender.public_id
		response['owner_id'] = tender.owner_id
		response['company_name'] = Extenstion.getCompanyName(tender.owner_id)
		response['created_at'] = Extenstion.convertDate(tender.created_at)
		response['category_id'] = tender.category_id
		response['title'] = tender.title.upper()
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

@app.route("/all/tenders")
@cache.memoize()
def Alltenders():
	Logger(request.method, request.endpoint, request.url, 'Listing all tenders', request.headers.get('User-Agent'), request.accept_languages)
	tenders = Tender.query.filter_by(status=5).all()
	data = []
	for tender in tenders:
		response = {}
		response['public_id'] = tender.public_id
		response['owner_id'] = tender.owner_id
		response['company_name'] = Extenstion.getCompanyName(tender.owner_id)
		response['created_at'] = Extenstion.convertDate(tender.created_at)
		response['category_id'] = tender.category_id
		response['title'] = tender.title.upper()
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


@app.route('/create/tender', methods=['POST'])
def createTender():
	print(request.mimetype)
	category_id = request.json['category_id']
	type_id = request.json['type_id']
	owner_id = request.json['owner_id']
	title = request.json['title']
	description = request.json['description']
	application_start_date = request.json['application_start_date']
	application_close_date = request.json['application_close_date']

	new_tender = Tender(
		public_id = str(uuid.uuid4()),
		category_id = category_id,
		type_id = type_id,
		owner_id = owner_id,
		title = title,
		tender_code = "T{}".format(str(uuid.uuid4())[:5]),
		description = description,
		application_start_date = application_start_date,
		application_close_date = application_close_date,
		created_at = datetime.now()
	)

	Tender.save_to_db(new_tender)
	# cache.delete('all_tenders')
	responseObject = { "message"  : "Successfully saved added the tender" } 
	return jsonify(responseObject), 200

@app.route('/tenders/<public_id>')
@cache.memoize()
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
		# response['amount'] = 'KES {:2,.2f}'.format(int(bid.amount))
		response['supplier'] = Extenstion.getUserName(bid.supplier_id)
		response['duration'] = bid.duration
		response['applied_at'] = Extenstion.convertDate(bid.created_at)
		response['public_id'] = bid.public_id
		response['docs'] = Extenstion.getBidDocuments(bid.public_id)
		bids.append(response)

	responseObject = {
			'public_id' : tender.public_id.upper(),
			'category_id' : tender.category_id,
			'title' : tender.title.upper(),
			'description' : tender.description,
			'application_start_date' : Extenstion.convertDate(tender.application_start_date),
			'application_close_date' : Extenstion.convertDate(tender.application_close_date),
			'category' :  Extenstion.getCategoryName(tender.category_id),
			'created_at' : Extenstion.convertDate(tender.created_at),
			'owner_id' : tender.owner_id,
			'company_name' : Extenstion.getCompanyName(tender.owner_id),
			'bids' : bids,
			'num_of_bids': len(bids),
			'docs' : Extenstion.getTenderDocuments(tender.public_id)
	}
	return jsonify(responseObject), 200

@app.route('/my/tenders/<public_id>')
@cache.memoize()
def getMyTenders(public_id):
	bids = Bid.query.filter_by(supplier_id=public_id).all()
	if not bids:
		return jsonify({'message' : 'No bids currently'}), 200
	
	tenders = []
	for bid in bids:
		response = {}
		response['amount'] = 'KES {:2,.2f}'.format(int(bid.amount))
		response['status'] = 'Received' if bid.status == 5 else "Acccepted"
		response['supplier'] = Extenstion.getUserName(bid.supplier_id)
		response['duration'] = bid.duration
		response['applied_at'] = Extenstion.convertDate(bid.created_at)
		response['public_id'] = bid.public_id
		response['tender'] = Extenstion.getTenderData(bid.tender_id)
		response['docs'] = Extenstion.getBidDocuments(bid.public_id)
		tenders.append(response)
	return jsonify(tenders), 200

@app.route('/org/tenders/<public_id>')
@cache.memoize()
def getOrgTenders(public_id):
	bids = Tender.query.filter_by(owner_id=public_id).all()
	if not bids:
		return jsonify({'message' : 'No tenders currently'}), 200
	
	tenders = []
	for bid in bids:
		response = {}
		response['category_id'] = bid.category_id
		response['category'] = Extenstion.getCategoryName(bid.category_id)
		response['status'] = 'Received' if bid.status == 5 else "Acccepted"
		response['application_start_date'] = Extenstion.convertDate(bid.application_start_date)
		response['application_close_date'] = Extenstion.convertDate(bid.application_close_date)
		response['applied_at'] = Extenstion.convertDate(bid.created_at)
		response['public_id'] = bid.public_id
		response['title'] = bid.title
		response['type_id'] = bid.type_id
		response['tender_code'] = (bid.tender_code).upper()
		response['docs'] = Extenstion.getTenderDocuments(bid.public_id)
		response['num_of_bids'] = Bid.query.filter_by(tender_id=bid.public_id).count()
		tenders.append(response)
	return jsonify(tenders), 200

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