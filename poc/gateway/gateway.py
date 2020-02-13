#!/usr/bin/env python3

from time import sleep

from flask import Flask, jsonify, url_for, request
from flask_restplus import Resource, Api, fields
import requests
from celery import Celery
from celery.task.control import inspect, revoke


# URL of your instance of SecurityRAT
SECRAT_URL = 'https://fe0vmc1201.de.bosch.com/' 
AZURE_MS_URL = 'http://localhost:5000'

# Interval in which the state of the evaluation should be checked (seconds)
CHECK_INTERVAL = 10

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
        "azure_tenant_id": fields.String(
            description="Tenant-id from Azure AD", required=True,
        ),
        "azure_subscription_id": fields.String(
            description="Subscription_id of azure subscription", required=True,
        ),
        "azure_client_id": fields.String(
            description="Client id from application for service principal",
            required=True,
        ),
        "azure_client_secret": fields.String(
            description="Client secret from application for service principal",
            required=True,
        ),
        "azure_resource": fields.String(
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

def trigger_azure_eval(requirement, test_properties):
    """Triggers the evaluation of given parameters with the azure microservice
    
    Parameters:
    requirement (dict): dictionary containing the properties of the "row" of securityRAT
    test_properties (dict): dictionary containing the elements of "testProperties" from "ScanDefinition"
    
    Returns:
    dict: dictionary containing the result of the test evaluation
    """
    
    eval_properties = {**test_properties}
    app.logger.info(eval_properties)
    
    # check if policy is there, then use the last part of it as id
    # last part of the passed url
    eval_properties["policy_id"] = requirement["policy_id"]
    
    # full URL of the policy
    eval_properties["policy_json_url"] = requirement["policy_json_url"]
    
    # use policy_id by default for now
    eval_properties["assignment_id"] = requirement["assignment_id"]
    
    r = requests.post(AZURE_MS_URL+'/api/tests', json=eval_properties)
    response = r.json()
    
    app.logger.info(response)
    
    status_url = f"{AZURE_MS_URL}/api/tests/{response['id']}"
    status_res = requests.get(status_url)
            
    while status_res.json().get("status", "ERROR") == "PENDING":
        sleep(CHECK_INTERVAL)
        status_res = requests.get(status_url)
    
    return status_res.json()

# delegating the scan to the microservice
@celery.task(bind=True)
def pass_scan(self, requirement, test_properties):
    result = {}
    
    if requirement["name"].startswith("MSA"):
        result = trigger_azure_eval(requirement, test_properties)
    
    if requirement["name"].startswith("AWS"):
        # TODO start AWS config rule evaluation
        pass
     
    return result
    

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
            task = pass_scan.apply_async(args=(requirement, request_params["testProperties"],))
            extra_headers['Location'] = "/scanapi/tests/" + task.id
            
            app.logger.info(task.id)
        
        return { "id": task.id }, 202, extra_headers
    
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
