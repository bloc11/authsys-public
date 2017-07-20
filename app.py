#!/usr/bin/env python
"""
"""

import time, os, base64, thread, urllib2, urllib, json

from sqlalchemy import create_engine, select, func

from authsys_common.model import members
from authsys_common.scripts import get_db_url, get_config, get_email_conf

eng = create_engine(get_db_url())
con = eng.connect()

from flask import Flask, request, jsonify, render_template
app = Flask(__name__, static_url_path='/static')

def payment_gateway_request():
    conf = get_config()
    url = "https://test.oppwa.com/v1/checkouts"
    data = {
        'authentication.userId' : conf.get('payment', 'userId'),
        'authentication.password' : conf.get('payment', 'password'),
        'authentication.entityId' : conf.get('payment', 'entityId'),
        'amount' : '92.00',
        'currency' : 'ZAR',
        'paymentType' : 'DB',
        'recurringType': 'INITIAL',
        'createRegistration': 'true',
        }
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, data=urllib.urlencode(data))
        request.get_method = lambda: 'POST'
        response = opener.open(request)
        return json.loads(response.read())
    except urllib2.HTTPError, e:
        return {'error': e.code}

def check_payment_status(path):
    conf = get_config()
    url = "https://test.oppwa.com/" + path
    params = "&".join(["%s=%s" for (k, v) in [
        ('authentication.userId', conf.get('payment', 'userId')),
        ('authentication.password', conf.get('payment', 'password')),
        ('authentication.entityId', conf.get('payment', 'entityId')),
    ]])
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url + "?" + params, data='')
        request.get_method = lambda: 'GET'
        response = opener.open(request)
        return json.loads(response.read())
    except urllib2.HTTPError, e:
        return {'error': e.code}


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

@app.route('/subscribe', methods=['GET'])
def subscribe():
    d = payment_gateway_request()
    if d.get('error') is not None:
        xxx # render error
    return render_template('subscribe.html', payment_id=d['id'])

@app.route('/subscribe_prep')
def subcribe_prep():
    return jsonify(payment_gateway_request())

@app.route('/finish')
def finish():
    status = check_payment_status(request.args['resourcePath'])
    res_code = status['result']['code']
    return render_template('finish.html', output=str(status))

@app.route('/update')
def update():
    user_id = request.args['id']
    name = list(con.execute(select([members.c.name]).where(members.c.id==user_id)))[0][0]
    return render_template('update.html', name=name, user_id=user_id)

@app.route('/submit', methods=["POST"])
def submit():
    con.execute(members.insert().values({
        'name': request.form['fullname'],
        'email': request.form['email'],
        'phone': request.form['phone'],
        'emergency_phone': request.form['emergency-phone'],
        'spam_consent': request.form.get('spam', 'off') == u'on',
        'id_number': request.form['id_no'],
        'signature_filename': request.form['filename'],
        'show_up_reason': request.form['reason'],
        'timestamp': int(time.time()),
    }))
    thread.start_new_thread(send_email, (request.form['email'],))
    return app.send_static_file('thankyou.html')

@app.route('/submit_details', methods=["POST"])
def submit_details():
    con.execute(members.update().values({
        'phone': request.form['phone'],
        'emergency_phone': request.form['emergency-phone'],
        'spam_consent': request.form.get('spam', 'off') == u'on',
        }).where(members.c.id==int(request.form['user_id'])))
    return app.send_static_file('thankyou.html')

@app.route('/')
def default():
    return app.send_static_file('index.html')
