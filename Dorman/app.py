
import os
import time
from flask import Flask, render_template, request, redirect, send_file,send_from_directory
from flask import session, flash,url_for, jsonify
from celery import Celery
from celery.task.control import revoke
import celery.states as states
from celery.exceptions import SoftTimeLimitExceeded

import sys
import imp
import logging
from urllib.parse import urlparse
from datetime import datetime
from scrapy.spiderloader import SpiderLoader
from scrapy.crawler import CrawlerRunner,CrawlerProcess
from twisted.internet import reactor
from scrapy import signals
from scrapy.utils.project import get_project_settings
from scrapy.utils.trackref import iter_all
from dormanproject import freeproxy
import pandas as pd
import xlrd
import time
import boto3
import logging
import json
from celery import task
from scrapy.exceptions import CloseSpider
from dormanproject.spiders.dormanspider import DormanSpider
from scrapy.utils.log import configure_logging
import random
from crochet import setup

logging.getLogger('scrapy').propagate = False

os.environ['SCRAPY_SETTINGS_MODULE'] = 'dormanproject.settings'

app = Flask(__name__)
UPLOAD_FOLDER = "/root/app/DormanProduct/uploads"
DOWNLOAD_FOLDER = "/root/app/DormanProduct/downloads"
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_REDIRECT_STDOUTS']=False
app.config['CELERY_REDIRECT_STDOUTS_LEVEL']= 'INFO'
ALLOWED_EXTENSIONS={'xlsx'}

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


def inputcodes(filepath):
    with open(filepath,'r'):
        df=pd.read_excel(filepath,usecols='A')
        productcodes=df['Compressed Old number'].to_list()
    return productcodes

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out


@app.route("/storage")
def storage():
    fileslist = make_tree(DOWNLOAD_FOLDER)
    file_path='/root/Dorman/scrapylog.log'
    if os.path.exists(file_path):
        f = open(file_path, "w")
        f.truncate()
        f.close()
    return render_template('storage.html', tree=fileslist)

def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])
    try: 
        lst = os.listdir(path)
        lst = sorted(lst,reverse=True)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                with open(fn,'rb') as f:
                    contents = f.read()
                tree['children'].append(dict(name=name, contents=contents))
    return tree

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=['POST'])
def upload():
    session.clear()
    global PROGRAM_INPUT
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No file chosen", 'danger')
            return redirect('/storage')
        f = request.files['file']
        if f.filename == '':
            flash('No selected file', 'danger')
            return redirect('/storage')
        elif not allowed_file(f.filename):
            flash('Incorrect file extenstion. Must be .xlsx!', 'danger')
            return redirect('/storage')
        f = request.files['file']
        f.save(os.path.join(UPLOAD_FOLDER, f.filename))
        PROGRAM_INPUT = os.path.join(UPLOAD_FOLDER, f.filename)
        flash("successfully uploaded the file","success")
        return redirect('/storage')


@app.route("/download/<path:filename>", methods=['GET'])
def download(filename):
    if request.method == "GET":
        return send_from_directory(directory=DOWNLOAD_FOLDER, filename=filename)


def output():
    output_filename = DOWNLOAD_FOLDER +"/dorman_output"
    fileIndex = 1
    fname = output_filename
    while os.path.isfile(fname + ".xlsx") == True:
        fname = "%s_%06d" % (output_filename, fileIndex)
        fileIndex = fileIndex + 1
    output_filename = fname
    return output_filename


@app.route('/stop')
def stopcrawl():
    global task
    if hasattr(task, 'revoke'):
        task.revoke(terminate=True,signal='QUIT')
        return redirect('/storage')
    else:
        return redirect('/storage')



@celery.task(bind=True)
def crawl(self,output_filename,input_filename,settings={},spider_name="dormanspider"):
    spider_kwargs=json.loads('{"input":"'+input_filename+'"}')
    project_settings = get_project_settings()
    project_settings.update({
        'DOWNLOAD_DIR': output_filename
        })
    logging.info('The file name for this run {}'.format(output_filename))
    spider_loader = SpiderLoader(project_settings)
    spider_cls = spider_loader.load(spider_name)
    process = CrawlerRunner(project_settings)
    try:
        if spider_kwargs.get("input"):
            spider_key = spider_kwargs.get("input")
            input_parse = inputcodes(spider_key)
            #num=len(input_parse)/10
            split_urls=chunkIt(input_parse,9)
            fp = freeproxy.WriteProxyList()
            fp.fetchandwriteproxy('/root/Dorman/dormanproject/proxyurl.lst')
            total = len(split_urls)
            verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
            adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
            noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
            message = ''
            flag = 1
            if not message or random.random() < 0.25:
                message = '{0} {1} {2}...'.format(random.choice(verb),random.choice(adjective),random.choice(noun))
            self.update_state(state='PROGRESS',meta={'current': flag, 'total': total,'status': message})
            setup()
            for index in split_urls:
                logging.info('the set of part codes to be run in iteration...{}'.format(index))
                flag = flag+1
                #for i in index:
                configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'},{'LOG_FILE': '/root/Dorman/scrapylog.log'})
                process.crawl(spider_cls,index)
                time.sleep(60)
                if not message or random.random() < 0.25:
                    message = '{0} {1} {2}...'.format(random.choice(verb),random.choice(adjective),random.choice(noun))
                self.update_state(state='PROGRESS',meta={'current':flag , 'total': total,'status': message})
                 
    except SystemExit:
        print("Task was stopped manually")
    except:
        print("Some other error occured during task execution")
        raise

@app.route('/streamout')
def streamout():
    def generate():
        with open('/root/Dorman/scrapylog.log') as f:
            while True:
                yield f.read()
                time.sleep(5)
    return app.response_class(generate(), mimetype='text/plain')



@app.route('/crawlurl', methods=['POST'])
def crawlurl():
    global task
    output_filename = output()
    input_filename = PROGRAM_INPUT
    task = crawl.apply_async(args=[output_filename,input_filename])
    return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}



@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = crawl.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        #print(task.info)
        if task.info == None:
            response = {
                'state': task.state,
                'current': 0,
                'total': 1,
                'status': '',
                'reason':''
                }
        else:
            response = {
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', '')
             }
            if 'result' in task.info:
                response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000,debug=True)
