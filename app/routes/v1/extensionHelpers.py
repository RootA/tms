from flask import Flask, jsonify, request, render_template, render_template_string, Markup
from routes.v1 import app, cache, db, Logger
import requests
# import sys
# sys.setrecursionlimit(10000)
from datetime import datetime, timedelta

from database.tenders import Category, Tender, Document, BidDocument
from database.users import User

class Extenstion:
	def getCategoryName(id):
		name, = db.session.query(Category.name).filter_by(public_id = id).first()
		return name if name else "N/A"
	
	def convertDate(timestamp):
		date = timestamp.strftime("%a, %b %Y")
		return date
	
	def cal_days_diff(a,b):
		A = a.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
		B = b.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
		return (A - B).days
	
	def getCompanyName(public_id):
		is_user= User.query.filter_by(public_id=public_id).first()
		if not is_user:
			return 'NA'
		return is_user.company_name

	
	def getUserName(id):
		response = {
			'fullname' : "Ruth Njeri",
			'email' : 'x@gmail.com',
			'phone_number' : '254899888832',
			'company' : "SafariIoT"
		}
		return response

	def getTenderData(id):
		tender = Tender.query.filter_by(public_id=id).first()

		if not tender:
			return "N/A"
		
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
			'owner' : Extenstion.getUserName(tender.owner_id)
		}
		return responseObject
	
	def getBidDocuments(id):
		docs = BidDocument.query.filter_by(bid_id=id).all()

		if not docs:
			return []
		
		files = []
		for doc in docs:
			response = {}
			response['doc_url'] = doc.doc_url
			files.append(response)
		
		return files

	def getTenderDocuments(id):
		docs = Document.query.filter_by(tender_id=id).all()

		if not docs:
			return []
		
		files = []
		for doc in docs:
			response = {}
			response['doc_url'] = doc.doc_url
			response['public_id'] = doc.public_id
			files.append(response)
		
		return files
