from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import jwt
from routes.v1 import db, app

class TimestampMixin(object):
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
	updated_at = db.Column(db.DateTime, default=datetime.now())
	deleted_at = db.Column(db.DateTime, default=datetime.now())

class BaseTracker(object):
	public_id = db.Column(db.String(100), primary_key=True)
	status = db.Column(db.Integer, nullable=False, default="5")
	deletion_marker = db.Column(db.Integer, nullable=True)
	created_by = db.Column(db.String(200), nullable=True, index=True)
	updated_by = db.Column(db.String(200), nullable=True, index=True)
	deleted_by = db.Column(db.String(200), nullable=True, index=True)