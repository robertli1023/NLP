# -*- coding:utf-8 -*-
from bottle import route, run, debug, template, request
import json
import requests, urllib
import test_5



@route('/get_say')
def get_say():
    saying = request.query.saying
    t = test_5.get_one_say_sentence(saying)
    print(t)
    return json.dumps(t)

@route('/')
def index():
    return template("template.html")

run(host='localhost', port=8080, debug=True)
