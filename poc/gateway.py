#!/usr/bin/env python3

import time

from flask import Flask, jsonify, url_for, request
from flask_restplus import Resource, Api, fields
import requests
from celery import Celery
from celery.task.control import inspect, revoke


app = Flask(__name__)

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

securityrat_url = 'https://fe0vmc1201.de.bosch.com/' # URL of your instance of SecurityRAT
microservice_url = 'http://localhost:5000'
api = Api(app)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
celery.conf.update(app.config)

ns = api.namespace('scanapi', description='Management of scans')

# necessary CORS headers
extra_headers = {'Access-Control-Allow-Origin': securityrat_url,'Access-Control-Allow-Methods': 'GET,POST,OPTIONS,DELETE',
                  'Access-Control-Allow-Headers': 'content-type, x-securitycat-csrf', 'Access-Control-Expose-Headers': 'Location', 'Vary': 'Origin'}

# Parameters given for a start of a scan
scan_definition = api.model('ScanDefinition', {
    'testProperties': fields.Nested(api.model('TestProperties', {
        'sonarKey': fields.String(
            description=u'SonarQube Key (if available)',
            required=False,
        ),
        'scmUrl': fields.String(
            description=u'Git repository URL (if available)',
            required=False,
        ),
        'appUrl': fields.String(
            description=u'Application URL (if available)',
            required=False,
        ),
    })),
    'requirements': fields.List(
        fields.String,
        required=True,
        description=u'List of requirements short names to test',
    ),
})


# delegating the scan to the microservice
@celery.task(bind=True)
def pass_scan(self, scan_pars):
    print(scan_pars)
    r = requests.post(microservice_url+'/scanapi/tests', json=scan_pars)
    response = r.json()
    return response


@ns.route('/tests')
class StartTest(Resource):
    @api.doc(responses={202: 'Scan was accepted, gives back the location header for fetching the result'})
    @api.expect(scan_definition)
    def post(self):
        """
        Starting a test
        """
        
        print(api.payload)
        request_params = api.payload
        task = pass_scan.apply_async(args=(request_params, ))
        extra_headers['Location'] = "/scanapi/tests/" + task.id
        return {}, 202, extra_headers
    
    @api.doc(False)
    def options(self):
        return {}, 200, extra_headers


# fetch the test result
@ns.route('/tests/<task_id>')
class TestResult(Resource):
    @api.doc(responses={200: 'Result of the scan'})
    def get(self, task_id):
        """
        Fetch the results of a test
        """
        task = pass_scan.AsyncResult(task_id)
        results = task.info
        if task.state == 'PENDING':
            time.sleep(3)
            task = pass_scan.AsyncResult(task_id)
            results = task.info
        # adapting to the expected output
        if task.state == "SUCCESS":
            for requirement in results:
                requirement['requirement'] = requirement.pop('req')
                result = requirement.pop('result')
                result['tool'] = 'custom_ms'
                requirement['testResults'] = []
                requirement['testResults'].append(result)
            return task.info, 200, extra_headers
        else:
            return {}, 500, extra_headers


    @api.doc(responses={200: 'Stop a running test.'})
    def delete(self, task_id):
        """
        Stopping a test
        """
        revoke(task_id, terminate=True)
    
    
    @api.doc(False)
    def options(self):
        return {}, 200, extra_headers


if __name__ == '__main__':
    app.run(debug=True, port=5001, ssl_context='adhoc')
