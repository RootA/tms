from flask import Flask, jsonify, request, render_template, render_template_string
from routes.v1 import app, cache, db, Logger, bcrypt
import requests, uuid, jwt
from flask_bcrypt import Bcrypt

from database.users import Usertype, User, Token
from .extensionHelpers import Extenstion

from datetime import datetime, timedelta

class OAuth:
	def createUserType(payload):
		name = payload['name'].upper()
		is_type = Usertype.query.filter_by(name=name).all()

		if is_type:
			return jsonify({'message':'That usertype already exists'}), 412
		
		new_type = Usertype(
			public_id = str(uuid.uuid4()),
			name = payload['name'],
			description = payload['description'],
			created_by = payload['session_id'],
			created_at = datetime.now(),
			updated_at = datetime.now()
		)
		Usertype.save_to_db(new_type)
		return jsonify({'message' : 'Successfully added the usertype'}), 200

	def getUsertypes():
		types = Usertype.query.filter(Usertype.deletion_marker == None).all()

		if not types:
			return jsonify({'mesage' : 'No usertypes found at this moment'}), 412

		types_array = []
		for data in types:
			response = {}
			response['name'] = data.name
			response['description'] = data.description
			response['public_id'] = data.public_id
			types_array.append(response)
		return jsonify({'data': types_array}), 200
	
	def userSignup(payload):
		if payload:
			password = '123456'
			# password = str(uuid.uuid4())[:10] # generates a random string to act as a system generated password
			u_ublic_id = str(uuid.uuid4())[:15]
			print("password", password)
			new_user = User(
				public_id = u_ublic_id,
				first_name = payload['first_name'],
				last_name = payload['last_name'],
				email = payload['email'],
				phone_number = payload['phone_number'],
				description = payload['description'],
				address = payload['address'],
				company_name = payload['company_name'],
				type_id = payload['type_id'],
				category_id = payload['category_id'],
				password = bcrypt.generate_password_hash(password, app.config['BCRYPT_LOG_ROUNDS']).decode('utf-8'),
				created_at = datetime.now()
			)
			User.save_to_db(new_user)
			
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
			Token.save_to_db(token)

			mail_payload = {
				'name' : '{} {}'.format(payload['first_name'], payload['last_name']),
				'confirm_account_url' : (app.config['CONFIRM_ACCOUNT_URL']).format(u_ublic_id),
				'link_url' : (app.config['CONFIRM_ACCOUNT_URL']).format(u_ublic_id),
				'product_name' : app.config['APP_NAME'],
				'company_name' : app.config['COMPANY_NAME']
			}

			# Send an Email
			sg = sendgrid.SendGridAPIClient(apikey=app.config['SENDGRID_API_KEY'])
			from_email = Email(app.config['MAIL_ADDRESS'])
			to_email = Email(payload['email'])
			subject = "Welcome to {}".format(app.config['APP_NAME'])
			content = Content("text/html", render_template('signup.html', data=mail_payload))
			mail = Mail(from_email, subject, to_email, content)
			
			try:
				response = sg.client.mail.send.post(request_body=mail.get())
			
				return jsonify({'message' : 'Welcome to {}, check your mail for your account details'.format(app.config['APP_NAME'])}), 200
			except Exception as e:
				return jsonify({"message": str(e)}), 422

			# return jsonify({'message' : 'Welcome to {}, check your mail for your account details'.format(app.config['APP_NAME'])}), 200

	def getAllUsers():
		users = User.query.all()

		if not users:
			return jsonify({'message' : 'No users found'}), 422

		data = []
		for user in users:
			response = {}
			user_type, = db.session.query(Usertype.name).filter_by(public_id=user.type_id).first()
			response['public_id'] = user.public_id
			response['first_name'] = user.first_name
			response['last_name'] = user.last_name
			response['email'] = user.email
			response['phone_number'] = user.phone_number
			response['user_type'] = user_type
			response['company_name'] = user.company_name
			response['created_at'] = Extenstion.convertDate(user.created_at)
			response['address'] = user.address
			response['status'] = "Active" if user.status == 5 else "Inactive"	
			data.append(response)
		return jsonify(data), 200	
