#!/usr/bin/env python
import os
import errno
import flask
from flask import request, Flask, redirect, url_for
from werkzeug import secure_filename
from urlparse import urlparse, urljoin

UPLOAD_FOLDER = './to_review'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'pdf'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#20MB file limit
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

def allowed_file(filename):
    return ('.' in filename) and filename.rsplit('.', 1)[1].lower() \
            in ALLOWED_EXTENSIONS
 
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

#TODO remove this route once deployed for real
#(form to submit should be in rails app)
@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/<id_type>', methods=['GET', 'POST'])
def upload_id(id_type):
    #TODO refactor this method
    if id_type not in ['id', 'payslip']:
        return redirect_back('failure')
    next = get_redirect_target()

    if request.method == 'POST':
        file = request.files['file']
        user_id = request.form["user"]
        #user_id = ''
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            root_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                        user_id, id_type) 
            mkdir_p(root_path)
            file.save(os.path.join(root_path, filename))
            return redirect(next)
    return '''
    <!doctype html>
    <title>File upload</title>
    Nothing to see here.
    '''

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target
        return ''

def is_safe_url(target):
    '''Is the url the same host as this server?
    
    Prevents malicious site phishing to look like something's
    succeeded on our end, when they control the redirect'''
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc

if __name__ == "__main__":
    app.debug = True
    app.run()
