from azure_interactor import AzureInteractor

tenant_id = '78ef7a7c-007b-47db-a268-1d8bc1f082dc'
subscription_id = '3a8b6402-45a2-4b9b-b6f7-73cbe8e507e2'
client_id = '9efa748e-d6ca-4476-9048-7ee22bbfdbc5'
client_secret = 'KPr02gMuz18zKVzf]laieTzyLpUtZ-?/'

interactor = AzureInteractor(tenant_id, subscription_id, client_id, client_secret)

policy_id = 'policyABCDEFGH'
definition_json = {
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

interactor.put_policy_definition(policy_id, definition_json)