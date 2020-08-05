import requests
from adal import AuthenticationContext

# context with the tenant-id from Azure AD
auth_context = AuthenticationContext(
    "https://login.microsoftonline.com/<tenant_id>"
)

SESSION = requests.Session()
# client id and secret from application (has to be assigned to the subscription)
token_response = auth_context.acquire_token_with_client_credentials(
    client_id="<client_id>",
    client_secret="<client_secret>",
    resource="https://management.azure.com/",
)

# add bearer token to the requests session
SESSION.headers.update({"Authorization": "Bearer " + token_response["accessToken"]})

# PUT assignment url
mgmt_policy_endpoint = "https://management.azure.com/subscriptions/<subscription_id>/providers/Microsoft.Authorization/policyAssignments/<policy_id>?api-version=2019-09-01"

data = {
    "properties": {
        "displayName": "[MSA-0.0.1] - Audit Windows VMs that do not store passwords using reversible encryption",
        "description": "",
        "metadata": {"assignedBy": "Tim Großmann"},
        "policyDefinitionId": "/subscriptions/<subscription_id>/providers/Microsoft.Authorization/policyDefinitions/<policy_id>",
        "enforcementMode": "Default",
        "parameters": {},
    }
}

headers = {"content-type": "application/json"}

# use json instead of data to send json data
out = SESSION.put(mgmt_policy_endpoint, json=data, headers=headers)
print(out.text)
