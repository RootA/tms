from flask import Flask, jsonify, request, render_template, render_template_string
from routes.v1 import app, cache, db, Logger, bcrypt
import requests
from flask_bcrypt import Bcrypt

from database.users import Usertype, User

from datetime import datetime, timedelta

class OAuth:
	def getUsertypes():
		types = Usertype.query.filter(Usertype.deletion_marker == None).all()

		if not types:
			return jsonify({'mesage' : 'No usertypes found at this moment'}), 412

		types_array = []
		for data in types:
			response = {}
			response['name'] = data.name
			response['description'] = data.description
			types_array.append(response)
		return types_array
	
	def userSignup(payload):
		if payload:
			password = str(uuid.uuid4())[:10] # generates a random string to act as a system generated password
			u_ublic_id = str(uuid.uuid4())[:15]
			new_user = User(
				public_id = u_ublic_id,
				first_name = payload['first_name'],
				last_name = payload['last_name'],
				email = payload['email'],
				phone_number = payload['phone_number'],
				description = payload['description'],
				company_name = payload['company_name'],
				type_id = payload['type_id'],
				category_id = payload['category_id'],
				password = bcrypt.generate_password_hash(password, app.config['BCRYPT_LOG_ROUNDS']).decode('utf-8'),
				created_at = datetime.now()
			)
			db.session.add(new_user)
			
			#generate and auth token 
			payload = {
				'exp' : datetime.utcnow() + timedelta(days=1, seconds=5),
				'iat': datetime.utcnow(),
				'sub': u_ublic_id
			}
			auth_token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
			token = Token(
				public_id = str(uuid.uuid4())[:8],
				token = auth_token.decode('utf-8'),
				user_public_id = u_ublic_id,
				client_id = 1,
				scopes = '[]',
				created_at = datetime.now()
			)
			db.session.add(token)
		
