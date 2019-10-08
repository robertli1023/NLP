# -*- coding:utf-8 -*-
from bottle import route, run, debug, template, request, static_file
import json
import requests, urllib
import test_5


@route('/get_saying')
def get_saying():
    saying = request.query.saying
    t = test_5.get_one_say_sentence(saying)
    print(t)
    return json.dumps(t)

@route('/')
def index():
    return template("template.html")

@route('/css/<filename>')
def css_static(filename):
    return static_file(filename, root='./css')

@route('/js/<filename>')
def js_static(filename):
    return static_file(filename, root='./js')
    
@route('/image/<filename>')
def js_static(filename):
    return static_file(filename, root='./image')

@route('/result/<filename>')
def get_json(filename):
    return static_file(filename, root='./result')

run(host='0.0.0.0', port=34567, debug=True)

