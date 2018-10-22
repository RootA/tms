from flask import Flask, jsonify, request, render_template, render_template_string
from routes.v1 import app, cache, db, Logger
import requests

# database imports
from database.users import Usertype, User

# class imports
from .oauthHelper import OAuth

@app.route('/users')
@cache.memoize()
def users():
    return OAuth.getAllUsers()

