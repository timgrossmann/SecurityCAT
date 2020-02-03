#!/usr/bin/env python3
import time
import requests
from flask import Flask, request, jsonify
from flask_restplus import Resource, Api, fields, reqparse
app = Flask(__name__)

api = Api(app)


# Parameters given for a start of a scan
scan_definition = api.model('ScanDefinition', {
    'testProperties' : fields.Nested(api.model('TestProperties', {
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

# Scan result structure
scan_result = api.model('ScanResultStructure', {
    'req': fields.String(description=u'Requirement ShortName'),
    'result' : fields.Nested(api.model('ScanResult', {
        'status': fields.String(description=u'Requirement fulfilled? (PASSED/FAILED/ERROR/IN_PROGRESS)'),
        'confidenceLevel': fields.Integer(description=u'Value in percent'),
        'message': fields.String(description=u'Result message')
    })),
})


### Scanning class
@api.route('/scanapi/tests', methods=['POST'])
class Scan(Resource):
    @api.doc(responses={200: 'Test result'})
    @api.expect(scan_definition)
    @api.marshal_list_with(scan_result)
    def post(self):
        request_params = api.payload
        target_url = request_params['testProperties']['appUrl']
        requirements = request_params['requirements']
        results = []   # array with test results
        request_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0'
        }
        response = requests.get(target_url, request_headers) # fetch the http response
        for req in requirements:
            output_res = {"req":req, 'result': {"message":"None", "status": "FAILED", "confidenceLevel": "0"}}
            if req == 'ASVS_3.0.1_10.10':
                if 'Public-Key-Pins' in response.headers:
                    output_res['result']['status'] = "PASSED"
                    output_res['result']['message'] = 'Detected HPKP Header with the value: \n```\n' + response.headers['Public-Key-Pins'] + '\n```'
                else:
                    output_res['result']['message'] = 'No pinning :('
                output_res['result']['confidenceLevel'] = 90
            elif req == 'ASVS_3.0.1_10.11':
                if 'Strict-Transport-Security' in response.headers:
                    output_res['result']['status'] = "PASSED"
                    output_res['result']['message'] = 'Detected HSTS Header with the value: \n```\n' +  response.headers['Strict-Transport-Security'] + '\n```'
                else:
                    output_res['result']['message'] = 'No HSTS :('
                output_res['result']['confidenceLevel'] = 90
            elif req == 'ASVS_3.0.1_10.12':
                if 'Strict-Transport-Security' in response.headers and 'preload' in response.headers['Strict-Transport-Security']:
                    output_res['result']['status'] = "PASSED"
                    output_res['result']['message'] = 'Preloading active: : \n```\n' +  response.headers['Strict-Transport-Security'] + '\n```'
                else:
                    output_res['result']['message'] = 'No preloading :('
                output_res['result']['confidenceLevel'] = 90
            else:
                output_res['result']['message'] = 'Unknown requirement'
                output_res['result']['status'] = 'ERROR'
            results.append(output_res)
        return results

if __name__ == '__main__':
    app.run(debug=True, port=5000)
