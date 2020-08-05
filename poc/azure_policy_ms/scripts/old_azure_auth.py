import requests
from adal import AuthenticationContext

auth_context = AuthenticationContext(
    "https://login.microsoftonline.com/<tenant_id>/"
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

# endpoints for policies

# definition
sub_policy_endpoint = "https://management.azure.com/subscriptions/<subscription_id>/providers/Microsoft.Authorization/policyDefinitions?api-version=2019-09-01"

# assignment
mgmt_policy_endpoint = "https://management.azure.com/providers/Microsoft.Management/managementgroups/mgmt-test/providers/Microsoft.Authorization/policyAssignments?%24filter=atScope()&api-version=2019-09-01"

# summarize
summarize_endpoint = "https://management.azure.com/subscriptions/<subscription_id>/providers/Microsoft.PolicyInsights/policyStates/latest/summarize?api-version=2018-04-04"

# trigger policy
trigger_endpoint = "https://management.azure.com/subscriptions/<subscription_id>/providers/Microsoft.PolicyInsights/policyStates/latest/triggerEvaluation?api-version=2018-07-01-preview"

data = {
    "$filter": "policyAssimentID eq '/subscriptions/<subscription_id>/providers/Microsoft.Authorization/policyDefinitions/<policy_def_id>'"
}

out = SESSION.post(summarize_endpoint, data=data)
print(out.text)


"""
data = {'filter': "policyAssimentID eq '/subscriptions/<subscription_id>/providers/Microsoft.Authorization/policyDefinitions/<policy_def_id>'"}

out = SESSION.post(trigger_endpoint, data=data)
print(out.headers['location'])


result_link = out.headers['location']
result_resp = SESSION.get(result_link)
print(result_resp)
"""
