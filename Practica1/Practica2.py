import json
import sqlite3
from hashlib import md5
from sqlite3 import Error

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return '<p>Hello, World!</p>'

@app.route('/hello/')
def hello():
    return '<p>Siiiiiii</p>'
@app.route('/hello/<name>')
def helloName(name):
    return "<p>Hola " + str(name) + "!!!</p"
def main():
    app.run(debug=True)




if __name__ == '__main__':
    main()
