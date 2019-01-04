from flask import Flask, jsonify, request, render_template, render_template_string, Markup, make_response
from routes.v1 import app, cache, db, Logger
import requests, uuid

from datetime import datetime, timedelta

from database.tenders import Category, Tender, Bid, BidDocument

from .extensionHelpers import Extenstion
from werkzeug.utils import secure_filename

import boto3, botocore
import boto, os
from boto.s3.key import Key
from botocore.client import Config

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

''' @param'''
@app.route('/bid', methods=['POST'])
def applyForTender():
	Logger(request.method, request.endpoint, request.url, 'tender application', request.headers.get('User-Agent'), request.accept_languages)

	tender_id = request.json['tender_id']
	supplier_id = request.json['session_id']
	amount = request.json['amount']
	duration = request.json['duration']
	
	tender = Tender.query.filter_by(public_id=tender_id).first()

	#Check if the supplier has applied for the bid before
	is_applied = Bid.query.filter_by(supplier_id=supplier_id, tender_id=tender_id).first()

	if is_applied:
		response = {
			'message' : "Looks like you've already applied for the {} tender".format(tender.title)
		}
		return jsonify(response), 422

	new_bid = Bid(
		public_id = str(uuid.uuid4()),
		created_at = datetime.now(),
		tender_id = tender_id,
		supplier_id = supplier_id,
		amount = amount,
		duration = duration
	)
	Bid.save_to_db(new_bid)
	response = {
		'message' : 'You have successfully applied for the tender'
	}
	return jsonify(response), 200

@app.route('/bid<public_id>')
def getBidInfo(public_id):
	bid = Bid.query.filter_by(public_id=public_id).filter(Bid.deletion_marker==None).first()

	if not bid:
		response = {'message' : 'No such bid can be found on our records'}
		return jsonify(response), 422
		
	responseObject = {
		'supplier_id' : bid.supplier_id,
		'supplier' : Extenstion.getUserName(bid.supplier_id),
		'amount' : 'KES {:2,.2f}'.format(int(bid.amount)),
		'duration' : bid.duration,
		'applied_at' : Extenstion.convertDate(bid.created_at),
		'public_id' : public_id,
		'docs' : Extenstion.getBidDocuments(bid.public_id)
	}
	return jsonify(responseObject), 200

@app.route('/my/bids/<public_id>')
def getMyBids(public_id):
	bids = Bid.query.filter_by(supplier_id=public_id).filter(Bid.deletion_marker==None).all()

	if not bids:
		response = {'message' : 'No bids can be found on our records'}
		return jsonify(response), 422
	
	data = []

	for bid in bids:
		response = {}
		response['public_id'] = bid.public_id
		response['applied_at'] = Extenstion.convertDate(bid.created_at)
		response['docs'] =  Extenstion.getBidDocuments(bid.public_id)
		response['amount'] = 'KES {:2,.2f}'.format(int(bid.amount))
		response['duration'] = bid.duration
		response['tender'] = Extenstion.getTenderData(bid.tender_id)
		response['status'] = 'Pending' if bid.status == 5 else "Awarded"
		data.append(response)

	return jsonify(data), 200

@app.route('/terminate/bid/<public_id>')
def terminateBid(public_id):
	bid = Bid.query.filter_by(public_id=public_id).filter(Bid.deletion_marker==None).first()

	if not bid:
		return jsonify({'message' : 'No such bid can be found'}), 412
	
	bid.status = 10 # denotes a user terminated bid
	db.session.commit()
	return jsonify({'message' : 'Termiated your bid'}), 200

@app.route('/bids')
def getAllBids():
	bids = Bid.query.filter(Bid.deletion_marker==None).all()

	if not bids:
		response = {'message' : 'No bids currently in the {} database'.format(app.config['APP_NAME'])}
		return jsonify(response), 422
	
	bid_data = []
	for bid in bids:
		response = {}
		response['supplier_id'] = bid.supplier_id
		response['amount'] = 'KES {:2,.2f}'.format(int(bid.amount))
		response['supplier'] = Extenstion.getUserName(bid.supplier_id)
		response['duration'] = bid.duration
		response['applied_at'] = Extenstion.convertDate(bid.created_at)
		response['public_id'] = bid.public_id
		response['tender'] = Extenstion.getTenderData(bid.tender_id)
		response['docs'] = Extenstion.getBidDocuments(bid.public_id)
		bid_data.append(response)
	
	return jsonify(bid_data), 200


@app.route('/bid/doc/upload/<public_id>', methods=['POST'])
def upload_file(public_id):
	Logger(request.method, request.endpoint, request.url, 'Bid Doc upload', request.headers.get('User-Agent'), request.accept_languages)

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

				bid = db.session.query(Bid).filter_by(public_id=public_id).first_or_404()

				if not bid:
					responseObject = {
						'message' : 'Bid does not exist'
					}
					return make_response(jsonify(responseObject)), app.config['ERROR_CODE']

				new_doc = BidDocument(
					public_id = str(uuid.uuid4()),
					created_at = datetime.now(),
					bid_id = public_id,
					doc_url = 'https://s3.eu-west-2.amazonaws.com/{0}/docs/{1}'.format(app.config['S3_BUCKET'], filename),
					doc_type = 'XYZ'
				)
				BidDocument.save_to_db(new_doc)
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
		return jsonify({'message' : 'File type not allowed'})

