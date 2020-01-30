import requests
from adal import AuthenticationContext

# context with the tenant-id from Azure AD
auth_context = AuthenticationContext('https://login.microsoftonline.com/78ef7a7c-007b-47db-a268-1d8bc1f082dc/')

SESSION = requests.Session()
# client id and secret from application (has to be assigned to the subscription)
token_response = auth_context.acquire_token_with_client_credentials(
    client_id='9efa748e-d6ca-4476-9048-7ee22bbfdbc5', 
    client_secret='KPr02gMuz18zKVzf]laieTzyLpUtZ-?/', 
    resource='https://management.azure.com/')

# add bearer token to the requests session
SESSION.headers.update({'Authorization': "Bearer " + token_response['accessToken']})

# PUT definition
sub_policy_endpoint = 'https://management.azure.com/subscriptions/3a8b6402-45a2-4b9b-b6f7-73cbe8e507e2/providers/Microsoft.Authorization/policyDefinitions/policy987654321?api-version=2019-09-01'

data = {
  "properties": {
    "displayName": "[EISA-ACC-201.4] - Audit Windows VMs that do not store passwords using reversible encryption",
    "policyType": "Custom",
    "mode": "All",
    "description": "This policy audits Windows virtual machines that do not store passwords using reversible encryption. This policy should only be used along with its corresponding deploy policy in an initiative/policy set. For more information on guest configuration policies, please visit http://aka.ms/gcpol",
    "metadata": {
      "category": "EISAServerOS"
    },
    "policyRule": {
      "if": {
        "allOf": [
          {
            "field": "type",
            "equals": "Microsoft.GuestConfiguration/guestConfigurationAssignments"
          },
          {
            "field": "name",
            "equals": "StorePasswordsUsingReversibleEncryption"
          },
          {
            "field": "Microsoft.GuestConfiguration/guestConfigurationAssignments/complianceStatus",
            "notEquals": "Compliant"
          }
        ]
      },
      "then": {
        "effect": "audit"
      }
    }
  }
}

headers = {
    "content-type":"application/json"
}

# use json instead of data to send json data
out = SESSION.put(sub_policy_endpoint, json=data, headers=headers)
print(out.text)
