from datetime import datetime, date
from flask import Flask, request, make_response
from google.cloud import datastore
from flask_restful import Api, Resource

app = Flask(__name__)
db = datastore.Client()

# curl
# hello/John -H 'Content-Type: application/json' -X PUT -d '{ "dateOfBirth": "2000-01-01" }'
#

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
        key = db.key('Name', userid)
        user_info = db.get(key)
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
        if not userid:
            return {"message": "User not provided"}, 200

        key = db.key('Name', userid)
        entity = datastore.Entity(key=key)
        entity.update(data)
        db.put(entity)
        resp = make_response('', 204)
        resp.headers['Content-Length'] = 0
        return resp


api = Api(app)
api.add_resource(Hello, "/hello/<string:userid>", endpoint="userid")

if __name__ == "__main__":
    app.run()