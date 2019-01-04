from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import jwt
from routes.v1 import db, app, clearCache, close
from .base import TimestampMixin, BaseTracker

class Category(db.Model, TimestampMixin, BaseTracker):
	name = db.Column(db.String(100), nullable=False)
	banner_img = db.Column(db.String(255), nullable=True)
	description = db.Column(db.Text)
	tenders = db.relationship('Tender', backref='category', lazy=True)

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		db.session.close()
		clearCache()

class Tag(db.Model, TimestampMixin, BaseTracker):
	name = db.Column(db.String(100), nullable=False)
	description = db.Column(db.Text)

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		db.session.close()
		clearCache()

class Type(db.Model, TimestampMixin, BaseTracker):
	name = db.Column(db.String(100), nullable=False)
	description = db.Column(db.Text)

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		db.session.close()
		clearCache()

class Tender(db.Model, TimestampMixin, BaseTracker):
	category_id = db.Column(db.String(100), db.ForeignKey('category.public_id'), nullable=False, index=True)
	type_id = db.Column(db.String(100), db.ForeignKey('type.public_id'), nullable=False, index=True)
	owner_id = db.Column(db.String(100), index=True)
	title = db.Column(db.String(100), nullable=False)
	description = db.Column(db.Text, nullable=False)
	application_start_date = db.Column(db.DateTime)
	application_close_date = db.Column(db.DateTime)
	tender_code = db.Column(db.String(20), index=True, unique=True)
	documents = db.relationship('Document', backref='tender', lazy=True)

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		db.session.close()
		clearCache()

class Document(db.Model, TimestampMixin, BaseTracker):
	tender_id = db.Column(db.String(100), db.ForeignKey('tender.public_id'), nullable=False)
	doc_type = db.Column(db.String(100), nullable=False)
	doc_url = db.Column(db.String(100), nullable=False)

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		db.session.close()
		clearCache()

class TagTender(db.Model, TimestampMixin, BaseTracker):
	tender_id = db.Column(db.String(100), db.ForeignKey('tender.public_id'), nullable=False, index=True)
	tag_id = db.Column(db.String(100), db.ForeignKey('tag.public_id'), nullable=False, index=True)

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		db.session.close()
		clearCache()

class Bid(db.Model, TimestampMixin, BaseTracker):
	tender_id = db.Column(db.String(100),  db.ForeignKey('tender.public_id'), nullable=False, index=True)
	supplier_id = db.Column(db.String(100), index=True)
	amount = db.Column(db.Float(6,2), nullable=True)
	duration = db.Column(db.Integer, nullable=False)
	awarded_at = db.Column(db.DateTime, default=datetime.now())
	awarded_by = db.Column(db.String(100))

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		db.session.close()
		clearCache()

class BidDocument(db.Model, TimestampMixin, BaseTracker):
	bid_id = db.Column(db.String(100), db.ForeignKey('bid.public_id'), nullable=False)
	doc_type = db.Column(db.String(100), nullable=True)
	doc_url = db.Column(db.String(100), nullable=False)

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		db.session.close()
		clearCache()


	

