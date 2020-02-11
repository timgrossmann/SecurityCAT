#!/usr/bin/env python3

import time

from flask import Flask, jsonify, url_for, request
from flask_restplus import Resource, Api, fields
import requests
from celery import Celery
from celery.task.control import inspect, revoke


# URL of your instance of SecurityRAT
SECRAT_URL = 'https://fe0vmc1201.de.bosch.com/' 
AZURE_MS_URL = 'http://localhost:5000'

app = Flask(__name__)
api = Api(app)

celery = Celery(app.name)
celery.config_from_object("celeryconfig")

ns = api.namespace('scanapi', description='Management of scans')

# necessary CORS headers
extra_headers = {'Access-Control-Allow-Origin': SECRAT_URL, 'Access-Control-Allow-Methods': 'GET,POST,OPTIONS,DELETE',
                  'Access-Control-Allow-Headers': 'content-type, x-securitycat-csrf', 'Access-Control-Expose-Headers': 'Location', 'Vary': 'Origin'}

# Parameters given for a start of a scan
scan_definition = api.model('ScanDefinition', {
    'testProperties': fields.Nested(api.model('TestProperties', {
        "tenantId": fields.String(
            description="Tenant-id from Azure AD", required=True,
        ),
        "subscriptionId": fields.String(
            description="Subscription_id of azure subscription", required=True,
        ),
        "clientId": fields.String(
            description="Client id from application for service principal",
            required=True,
        ),
        "clientSecret": fields.String(
            description="Client secret from application for service principal",
            required=True,
        ),
        "resource": fields.String(
            description="Optional url endpoint of azure resource ([default] 'https://management.azure.com/')",
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
def pass_scan(self, requirement, test_properties):
    # starting the evaluation, get back eval_id of test
    
    """Add to json:
            "policyId": fields.String(
        description="Unique identifier for policy definition", required=True,
        ),
        "policyJsonUrl": fields.String(
            description="URL of the json policy definition in the format of https://docs.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure",
            required=True,
        ),
        "assignmentId": fields.String(
            description="Optional unique identifier for policy assignment (policyId will be used if not given)",
            required=False,
        ),
    """
    
    # One task per requirement
    # where to get the additional parameters for each test?
    
    if requirement.startsWith("MSA"):
        app.logger.info("Azure check")
        r = requests.post(AZURE_MS_URL+'/scanapi/tests', json=test_properties)
        response = r.json()
    
    # TODO wait for evaluation to finish before returning in order to work with celery
    # call given eval_id on get of azure_ms
    
    return response


@ns.route('/tests')
class StartTest(Resource):
    @api.doc(responses={202: 'Scan was accepted, gives back the location header for fetching the result'})
    @api.expect(scan_definition)
    def post(self):
        """
        Starting a test
        """
        
        app.logger.info(api.payload)
        request_params = api.payload
        
        # filter requirements for ones for azure_ms
        # delegate azure requirements to azure_ms
        
        for requirement in request_params["requirements"]:
            task = pass_scan.apply_async(args=(requirement, request_params["testProperties"]))
            extra_headers['Location'] = "/scanapi/tests/" + task.id
            
            app.logger.info(task.id)
        
        return {}, 202, extra_headers
    
    @api.doc(False)
    def options(self):
        return {}, 200, extra_headers


# fetch the test result
@ns.route('/tests/<task_id>')
@ns.param('task_id', 'The task identifier')
class TestResult(Resource):
    @api.doc(responses={200: 'Result of the scan'})
    def get(self, task_id):
        """
        Fetch the results of a test
        """
        task = pass_scan.AsyncResult(task_id)
        results = task.info
        
        app.logger.info(f"Called with it {task}")
        
        # if evaluation is not yet done, tell secrat to check back again
        if task.state == 'PENDING':
            return { 'status': 'PENDING' }, 200, extra_headers
            
        # adapting to the expected output
        if task.state == "SUCCESS":
            for requirement in results:
                requirement['requirement'] = requirement.pop('req')
                result = requirement.pop('result')
                result['tool'] = 'custom_ms'
                requirement['testResults'] = []
                requirement['testResults'].append(result)
            return task.info, 200, extra_headers


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
    app.run(debug=True, port=5001)
