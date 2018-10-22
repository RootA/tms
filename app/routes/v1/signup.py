from flask import Flask, jsonify, request, render_template, render_template_string
from routes.v1 import app, cache, db, Logger
import requests

# database imports
from database.users import Usertype, User

# class imports
from .oauthHelper import OAuth

@app.route('/add/type', methods=['POST'])
def addType():
	name = request.json['name']
	description = request.json['description']
	session_id = request.json['session_id']

	empty_set = []
	if not name:
		empty_set.append('Name is required')
	
	if empty_set:
		return jsonify({'message' : empty_set}), 412
	
	payload = {
		'name' : name,
		'description' : description,
		'session_id' : session_id
	}
	return OAuth.createUserType(payload)

	
@app.route('/usertypes')
def usertypes():
	return OAuth.getUsertypes()

@app.route('/signup', methods=['POST'])
def signup():
	first_name = request.json['first_name']
	last_name = request.json['last_name']
	email = request.json['email']
	phone_number = request.json['phone_number']
	category_id = request.json['category_id']
	user_type = request.json['user_type']
	company_name = request.json['company_name']
	address = request.json['address']
	description = request.json['description']

	#check if the user exists
	is_user = User.query.filter_by(email=email, phone_number=phone_number).first()

	if is_user:
		return jsonify({'message' : 'The email or phone number is already in use'}), 422
	
	try:
		#continue with registration
		payload = {
			'first_name' : first_name,
			'last_name' : last_name,
			'email' : email,
			'address' : address,
			'phone_number' : phone_number,
			'description' : description,
			'company_name' : company_name,
			'type_id': user_type,
			'category_id' : category_id
		}
		return OAuth.userSignup(payload)
	except Exception as identifier:
		return jsonify({'message' : str(identifier)}), 500
