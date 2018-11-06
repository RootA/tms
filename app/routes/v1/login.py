from flask import Flask, jsonify, request, render_template, render_template_string, flash
from routes.v1 import app, cache, db, Logger, bcrypt
import requests

# database imports
from database.users import Usertype, User

# class imports
from .oauthHelper import OAuth

@app.route('/login', methods=['POST'])
def getLogin():
	email = request.json['email']
	password = request.json['password']

	is_user = User.query.filter_by(email=email, status=5).first()

	if not is_user:
		return jsonify({'message':'To create and account head to the signup page '}), 412
	
	if is_user and bcrypt.check_password_hash(is_user.password, password):
		auth_token = is_user.encode_auth_token(is_user.public_id)
		if auth_token:
			responseObject = {
				'public_id' : is_user.public_id,
				'first_name' : is_user.first_name,
				'last_name' : is_user.last_name,
				'email' : is_user.email,
				'phone_number' : is_user.phone_number,
				'full_name' : '{} {}'.format(is_user.first_name, is_user.last_name),
				'company_name' : is_user.company_name,
				'user_type' : db.session.query(Usertype.name).filter_by(public_id=is_user.type_id).first()[0],
				'auth_token' :  auth_token.decode(),
				'type_id' : is_user.type_id
			}
			return jsonify(responseObject), 200
	return jsonify({'message' : 'Invalid credentials'}), 422
	
