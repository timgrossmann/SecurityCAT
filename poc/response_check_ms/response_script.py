"""
PoC-Implementation of Header checking from:
https://github.com/SecurityRAT/SecurityCAT-PoC/blob/master/microservice.py
"""

request_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0'
}

response = requests.get(target_url, request_headers) # fetch the http response
for req in requirements: # requirements passed from over gateway from securityRAT
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