# -*- coding: utf-8 -*-
from flask import Flask, jsonify, url_for, redirect, request
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
import os
from datetime import datetime, date

app = Flask(__name__)
mongoip = os.environ['MONGODB_IP']
mongodb = os.environ.get('MONGODB_DB', 'hello')
mongouser = os.environ.get('MONGODB_USER', 'admin')
mongopass  = os.environ.get('MONGODB_PASSWORD', 'password')

app.config["MONGO_URI"] = "mongodb://{}:{}@{}:27017/{}".format(mongouser, mongopass, mongoip, mongodb)
mongo = PyMongo(app)
# ---

def calc_days_to_birthday(birthday_str):
    date_format = "%Y-%m-%d"
    bday = datetime.strptime(birthday_str, date_format).date()
    now = date.today()
    nextBirthday = date(now.year,bday.month, bday.day)
    if now == nextBirthday:
        return 0
    if now<nextBirthday:
        return (nextBirthday - now).days
    else:
        nextBirthday = date(now.year+1, bday.month, bday.day)
        return (nextBirthday - now).days

class Hello(Resource):
    def get(self, id=None):
        if id:
            user_info = mongo.db.hello.find_one({"id": id}, {"_id": 0})
            if user_info:
                user_date = user_info.get('dateOfBirth', None)
                if user_date:
                    days = calc_days_to_birthday(user_date)
                    if days == 0:
                        message = "Hello, {}! Happy birthday!".format(id)
                    else:
                        message = "Hello, {}! Your birthday is in {} days.".format(id, days)
                    return {"message": message}, 200
        # Finally if any errors
        return {"message": "no data found for {}".format(id)}, 200

    def put(self, id):
        data = request.get_json()
        mongo.db.hello.update_one({'id': id}, {'$set': data}, upsert=True)
        return '', 204

# ---
api = Api(app)
api.add_resource(Hello, "/hello/<string:id>", endpoint="id")

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)