from flask import Flask, jsonify, request, render_template, render_template_string, flash
from routes.v1 import app, cache, db, Logger
import requests

# database imports
from database.users import Usertype, User

# class imports
from .oauthHelper import OAuth

@app.route('/login')
def getLogin():
	# flash("welcome to the login page")
	return render_template('login.html')