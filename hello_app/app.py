# -*- coding: utf-8 -*-
import os
from datetime import datetime, date

from flask import Flask, jsonify, url_for, redirect, request
from flask_pymongo import PyMongo
from flask_restful import Api, Resource

app = Flask(__name__)
mongoip = os.environ['MONGODB_IP']
mongodb = os.environ.get('MONGODB_DB', 'hello')
mongouser = os.environ.get('MONGODB_USER', 'admin')
mongopass = os.environ.get('MONGODB_PASSWORD', 'password')

app.config["MONGO_URI"] = "mongodb://{}:{}@{}:27017/{}".format(mongouser, mongopass, mongoip, mongodb)
mongo = PyMongo(app)


def calc_days_to_birthday(birthday_str):
    date_format = "%Y-%m-%d"
    bday = datetime.strptime(birthday_str, date_format).date()
    now = date.today()
    next_bday = date(now.year, bday.month, bday.day)
    if now == next_bday:
        return 0
    if now < next_bday:
        return (next_bday - now).days
    else:
        next_bday = date(now.year + 1, bday.month, bday.day)
        return (next_bday - now).days


class Hello(Resource):
    def get(self, userid=None):
        if not userid:
            return {"message": "User not provided"}, 200

        message = "no data found for {}".format(userid)
        user_info = mongo.db.hello.find_one({"id": userid}, {"_id": 0})
        if not user_info:
            return {"message": message}, 200

        user_date = user_info.get('dateOfBirth', None)
        if not user_date:
            return {"message": message}, 200

        days = calc_days_to_birthday(user_date)
        if days == 0:
            message = "Hello, {}! Happy birthday!".format(userid)
        else:
            message = "Hello, {}! Your birthday is in {} days.".format(userid, days)
        return {"message": message}, 200

    def put(self, userid):
        data = request.get_json()
        mongo.db.hello.update_one({'id': userid}, {'$set': data}, upsert=True)
        return '', 204


api = Api(app)
api.add_resource(Hello, "/hello/<string:userid>", endpoint="userid")

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
