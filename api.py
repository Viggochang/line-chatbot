#!/usr/bin/python
# -*- coding: utf-8 -*-

import flask
from flask import jsonify, request
import pandas as pd
import numpy 

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["JSON_AS_ASCII"] = False

# test data
tpe = {
    "id": 0,
    "city_name": "台北",
    "country_name": "台灣",
    "is_capital": True,
    "location": {
        "longitude": 121.569649,
        "latitude": 25.036786
    }
}
nyc = {
    "id": 1,
    "city_name": "紐約",
    "country_name": "美國",
    "is_capital": False,
    "location": {
        "longitude": -74.004364,
        "latitude": 40.710405
    }
}
ldn = {
    "id": 2,
    "city_name": "倫敦",
    "country_name": "英國",
    "is_capital": True,
    "location": {
        "longitude": -0.114089,
        "latitude": 51.507497
    }
}
cities = [tpe, nyc, ldn]

gapminder = pd.read_csv("gapminder.csv")
gapminder_list = []
type_tran = {numpy.float64:float, numpy.int64:int}

for i in range(gapminder.shape[0]):
    g = gapminder.loc[i,:]
    temp = {}
    for index, value in zip(g.index, g.values):
        if type(value) in type_tran.keys():
            value = type_tran[type(value)](value)
        temp[index] = value
    gapminder_list.append(temp) 
    

@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello Flask!</h1>"

@app.route('/cities/all', methods=['GET'])
def cities_all():
    return jsonify(cities)

# http://127.0.0.1:5000/cities?city_name=台北
@app.route('/cities', methods=['GET'])
def city_name():
    if 'city_name' in request.args:
        city_name = request.args['city_name']
    else:
        return "Error: No city_name provided. Please specify a city_name."
    results = []

    for city in cities:
        if city_name == city['city_name']:
            results.append(city)

    return jsonify(results)

# http://127.0.0.1:5000/cities/台北
@app.route('/cities/<string:city_name>')
def city_name_b(city_name):
    results = []
    for city in cities:
        if city_name == city['city_name']:
            results.append(city)
    return jsonify(results)

@app.route('/gapminder/all', methods=['GET'])
def gapminder_all():
    return jsonify(gapminder_list)

@app.route('/gapminder', methods=['GET'])
def country():
    if "country" not in request.args:
        return "Error: No country provided. Please specify a country."

    print()
    result = [request.args["country"]]
    for g in gapminder_list:
        if request.args["country"] == g["country"]:
            result.append(g)
        
    return jsonify(result)    

app.run()
