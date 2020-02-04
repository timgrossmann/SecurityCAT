import requests
from adal import AuthenticationContext

# context with the tenant-id from Azure AD
auth_context = AuthenticationContext(
    "https://login.microsoftonline.com/78ef7a7c-007b-47db-a268-1d8bc1f082dc/"
)

SESSION = requests.Session()
# client id and secret from application (has to be assigned to the subscription)
token_response = auth_context.acquire_token_with_client_credentials(
    client_id="9efa748e-d6ca-4476-9048-7ee22bbfdbc5",
    client_secret="KPr02gMuz18zKVzf]laieTzyLpUtZ-?/",
    resource="https://management.azure.com/",
)

# add bearer token to the requests session
SESSION.headers.update({"Authorization": "Bearer " + token_response["accessToken"]})

# POST trigger policy
trigger_endpoint = "https://management.azure.com/subscriptions/3a8b6402-45a2-4b9b-b6f7-73cbe8e507e2/providers/Microsoft.PolicyInsights/policyStates/latest/triggerEvaluation?api-version=2019-09-01"

data = {
    "$filter": "policyAssignmentId eq '/subscriptions/3a8b6402-45a2-4b9b-b6f7-73cbe8e507e2/providers/Microsoft.Authorization/policyAssignments/6dd881dee049489888d7e22e'"
}

headers = {"content-type": "application/json"}

"""
# trigger evaluation, get back url to check evaluation state
# https://docs.microsoft.com/en-us/azure/governance/policy/how-to/get-compliance-data#on-demand-evaluation-scan
out = SESSION.post(trigger_endpoint, json=data, headers=headers)
print(out.headers['location'])

# get evaluation state for execution (202 if going, 200 if succeeded) => get summary after
result_link = out.headers['location']
result_resp = SESSION.get(result_link)
print(result_resp)
"""

"""
from time import sleep
from datetime import datetime
print('started' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

while True:    
    result = SESSION.get('https://management.azure.com/subscriptions/3a8b6402-45a2-4b9b-b6f7-73cbe8e507e2/providers/Microsoft.PolicyInsights/asyncOperationResults/eyJpZCI6IlBTUkFKb2I6MkQ1MTkwNkE3RiIsImxvY2F0aW9uIjoiIn0?api-version=2018-07-01-preview')
    
    if result.status_code == 200:
        break;
        
    print(result.status_code)
        
    sleep(10)

print('end' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
"""
