#!/usr/bin/env python
import os
import flask
from werkzeug import secure_filename
from urlparse import urlparse, urljoin

UPLOAD_FOLDER = './to_review'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'pdf'])

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#20MB file limit
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

def allowed_file(filename):
    return ('.' in filename) and filename.rsplit('.', 1) in ALLOWED_EXTENSIONS

@app.route('/<id_type>', methods=['GET', 'POST'])
def upload_id(id_type):
    if id_type is not in ['id', 'payslip']:
        return

    next = get_redirect_target()
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 
                        id_type, filename))
            return redirect_back()
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
