import requests
from adal import AuthenticationContext

# context with the tenant-id from Azure AD
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

# PUT definition
sub_policy_endpoint = "https://management.azure.com/subscriptions/<subscription_id>/providers/Microsoft.Authorization/policyDefinitions/<policy_id>?api-version=2019-09-01"

data = {
    "properties": {
        "displayName": "[MSA-0.0.1] - Windows VMs that do not store passwords using encryption",
        "policyType": "Custom",
        "mode": "All",
        "description": "This policy audits Windows virtual machines that do not store passwords using reversible encryption.",
        "metadata": {"category": "MSA-OS"},
        "policyRule": {
            "if": {
                "allOf": [
                    {
                        "field": "type",
                        "equals": "Microsoft.GuestConfiguration/guestConfigurationAssignments",
                    },
                    {
                        "field": "name",
                        "equals": "StorePasswordsUsingReversibleEncryption",
                    },
                    {
                        "field": "Microsoft.GuestConfiguration/guestConfigurationAssignments/complianceStatus",
                        "notEquals": "Compliant",
                    },
                ]
            },
            "then": {"effect": "audit"},
        },
    }
}

headers = {"content-type": "application/json"}

# use json instead of data to send json data
out = SESSION.put(sub_policy_endpoint, json=data, headers=headers)
print(out.text)
