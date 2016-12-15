#!/usr/bin/env python
"""
"""

import time, os, base64, thread

from sqlalchemy import create_engine, select, func

from authsys_common.model import members
from authsys_common.scripts import get_db_url, get_config, get_email_conf

eng = create_engine(get_db_url())
con = eng.connect()

from flask import Flask, request
app = Flask(__name__, static_url_path='/static')

def send_email(target):
    import smtplib
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(*get_email_conf())
    msg = """Subject: Welcome to bloc 11
From: bloc.eleven@gmail.com

%s
""" % open(os.path.join(os.path.dirname(__file__), 'letter.txt')).read()
    server.sendmail("bloc.eleven@gmail.com", target, msg)

@app.route("/upload_signature", methods=["POST"])
def upload_sign():
    # pretty sure it's not how you do it....
    d = request.form.keys()[0]
    prefix = "data:image/png;base64,"
    assert d.startswith(prefix)
    store_dir = get_config().get('data', 'store_dir')
    # invent new filename
    no = list(con.execute(select([func.count(members)])))[0][0]
    fname = os.path.join(store_dir, "signature_%d.png" % int(no))
    d = d[len(prefix):]
    if (len(d) % 4) != 0:
        d += "=" * (4 - (len(d) % 4))
    with open(fname, "w") as f:
        f.write(base64.b64decode(d, " /"))
    return fname

@app.route('/submit', methods=["POST"])
def submit():
    con.execute(members.insert().values({
        'name': request.form['fullname'],
        'email': request.form['email'],
        'spam_consent': request.form.get('spam', 'off') == u'on',
        'id_number': request.form['id_no'],
        'signature_filename': request.form['filename'],
        'timestamp': int(time.time()),
    }))
    thread.start_new_thread(send_email, (request.form['email'],))
    return app.send_static_file('thankyou.html')

@app.route('/')
def default():
    return app.send_static_file('index.html')
