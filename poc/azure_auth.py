import requests
from adal import AuthenticationContext

auth_context = AuthenticationContext('https://login.microsoftonline.com/78ef7a7c-007b-47db-a268-1d8bc1f082dc/')

SESSION = requests.Session()
# client id and secret from application (has to be assigned to the subscription)
token_response = auth_context.acquire_token_with_client_credentials(
    client_id='9efa748e-d6ca-4476-9048-7ee22bbfdbc5', 
    client_secret='KPr02gMuz18zKVzf]laieTzyLpUtZ-?/', 
    resource='https://management.azure.com/')

SESSION.headers.update({'Authorization': "Bearer " + token_response['accessToken']})

sub_policy_endpoint = 'https://management.azure.com/subscriptions/3a8b6402-45a2-4b9b-b6f7-73cbe8e507e2/providers/Microsoft.Authorization/policyDefinitions?api-version=2019-09-01'
mgmt_policy_endpoint = 'https://management.azure.com/providers/Microsoft.Management/managementgroups/mgmt-test/providers/Microsoft.Authorization/policyAssignments?%24filter=atScope()&api-version=2019-09-01'

json_out = SESSION.get(mgmt_policy_endpoint).json()
print(json_out)