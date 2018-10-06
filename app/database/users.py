from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import jwt
from routes.v1 import db, app, clearCache, close
from .base import TimestampMixin, BaseTracker
from .tenders import Category

class Usertype(db.Model, TimestampMixin, BaseTracker):
	name = db.Column(db.String(100), nullable=False)
	description = db.Column(db.Text)

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		clearCache()
		close(db)
	
class User(db.Model, TimestampMixin, BaseTracker):
	type_id = db.Column(db.String(100), db.ForeignKey('usertype.public_id') ,nullable=False)
	category_id = db.Column(db.String(100), db.ForeignKey('category.public_id'), nullable=False, index=True)
	first_name = db.Column(db.String(100), nullable=False)
	last_name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False)
	phone_number = db.Column(db.String(100), nullable=False)
	company_name = db.Column(db.String(200))
	address = db.Column(db.String(200))
	description = db.Column(db.String(200))
	password = db.Column(db.String(150), nullable=False)

	def encode_auth_token(self, user_id):
		"""
		Generates the Auth Token
		:return: string
		"""
		try:
			payload = {
				'exp': datetime.utcnow() + timedelta(days=1, seconds=5),
				'iat': datetime.utcnow(),
				'sub': user_id
			}
			return jwt.encode(
				payload,
				app.config.get('SECRET_KEY'),
				algorithm='HS256'
			)
		except Exception as e:
			return e

	@staticmethod
	def decode_auth_token(auth_token):
		"""
		Validates the auth token
		:param auth_token:
		:return: integer|string
		"""
		try:
			payload = jwt.decode(auth_token, app.config['SECRET_KEY'], 'utf-8')
			is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
			if is_blacklisted_token:
				return 'Token blacklisted. Please log in again.'
			else:
				return payload['sub']
		except jwt.ExpiredSignatureError:
			return 'Signature expired. Please log in again.'
		except jwt.InvalidTokenError:
			return 'Invalid token. Please log in again.'
		
	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		clearCache()
		close(db)

class OAuthClient(db.Model, TimestampMixin):
	id = db.Column(db.Integer, primary_key=True)
	user_public_id = db.Column(db.String(100), nullable=True)
	name = db.Column(db.String(100), nullable=True)
	secret = db.Column(db.String(100))
	redirect = db.Column(db.Text, nullable=True)
	personal_access_client = db.Column(db.Integer)
	password_client = db.Column(db.Integer)
	revoked = db.Column(db.Integer)

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		clearCache()
		close(db)

class Token(db.Model, TimestampMixin):
	id = db.Column(db.Integer, primary_key=True)
	public_id = db.Column(db.String(100), nullable=False)
	user_public_id = db.Column(db.String(100), db.ForeignKey('user.public_id'), index=True)
	token = db.Column(db.Text, nullable=False)
	client_id = db.Column(db.Integer, nullable=True)
	scopes = db.Column(db.Text, nullable=True)
	revoked = db.Column(db.Integer, nullable=True)

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		clearCache()
		close(db)

class PasswordReset(db.Model, TimestampMixin):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), nullable=False)
	token = db.Column(db.Text, nullable=False, unique=True, index=True)
	public_id  = db.Column(db.String(100), nullable=False, index=True, unique=True)

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		clearCache()
		close(db)