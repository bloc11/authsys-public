#!/usr/bin/env python
"""
"""

from sqlalchemy import create_engine

from authsys_common.model import indemnity_forms
from authsys_common.scripts import get_db_url

eng = create_engine(get_db_url())
con = eng.connect()

from flask import Flask
app = Flask(__name__, static_url_path='/static')

@app.route('/')
def hello_world():
    return app.send_static_file('index.html')
