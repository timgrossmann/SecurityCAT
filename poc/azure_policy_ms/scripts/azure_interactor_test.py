from azure_interactor import AzureInteractor

tenant_id = "<tenant_id>"
subscription_id = "<subscription_id>"
client_id = "<client_id>"
client_secret = "<client_secret>"

interactor = AzureInteractor(tenant_id, subscription_id, client_id, client_secret)

policy_id = "policyABCDEFGH"
definition_json = {
    "properties": {
        "displayName": "[MSA-0.0.01] - Audit Windows VMs that do not store passwords using encryption",
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

"""
print(interactor.put_policy_definition(policy_id, definition_json).text)
print()
print(interactor.put_policy_assignment(policy_id, policy_id))
print()
check_loc = interactor.trigger_policy().headers["location"]
print(check_loc)
print(interactor.wait_for_eval_complete(check_loc))
"""

print(
    interactor.get_policy_eval_summary("<id>").json()["value"][0][
        "results"
    ]
)


"""
{
   "@odata.context":"https://management.azure.com/subscriptions/<subscription_id>/providers/Microsoft.Authorization/policyAssignments/<policy_assignment_id>/providers/Microsoft.PolicyInsights/policyStates/$metadata#summary",
   "@odata.count":1,
   "value":[
      {
         "@odata.id":null,
         "@odata.context":"https://management.azure.com/subscriptions/<subscription_id>/providers/Microsoft.Authorization/policyAssignments/<policy_assignment_id>/providers/Microsoft.PolicyInsights/policyStates/$metadata#summary/$entity",
         "results":{
            "queryResultsUri":"https://management.azure.com/subscriptions/<subscription_id>/providers/Microsoft.Authorization/policyAssignments/<policy_assignment_id>/providers/Microsoft.PolicyInsights/policyStates/latest/queryResults?api-version=2019-10-01&$from=2020-02-05 12:27:27Z&$to=2020-02-06 12:27:27Z",
            "nonCompliantResources":1,
            "nonCompliantPolicies":1,
            "resourceDetails":[
               {
                  "complianceState":"noncompliant",
                  "count":1
               }
            ],
            "policyDetails":[
               {
                  "complianceState":"noncompliant",
                  "count":1
               }
            ],
            "policyGroupDetails":[
               {
                  "complianceState":"noncompliant",
                  "count":1
               }
            ]
         },
         "policyAssignments":[
            {
               "policyAssignmentId":"/subscriptions/<subscription_id>/providers/microsoft.authorization/policyassignments/<policy_assignment_id>",
               "policySetDefinitionId":"",
               "results":{
                  "queryResultsUri":"https://management.azure.com/subscriptions/<subscription_id>/providers/Microsoft.Authorization/policyAssignments/<policy_assignment_id>/providers/Microsoft.PolicyInsights/policyStates/latest/queryResults?api-version=2019-10-01&$from=2020-02-05 12:27:27Z&$to=2020-02-06 12:27:27Z and PolicyAssignmentId eq '/subscriptions/3a8b6402-45a2-4b9b-b6f7-73cbe8e507e2/providers/microsoft.authorization/policyassignments/6dd881dee049489888d7e22e'",
                  "nonCompliantResources":1,
                  "nonCompliantPolicies":1,
                  "resourceDetails":[
                     {
                        "complianceState":"noncompliant",
                        "count":1
                     }
                  ],
                  "policyDetails":[
                     {
                        "complianceState":"noncompliant",
                        "count":1
                     }
                  ],
                  "policyGroupDetails":[
                     {
                        "complianceState":"noncompliant",
                        "count":1
                     }
                  ]
               },
               "policyDefinitions":[
                  {
                     "policyDefinitionGroupNames":[
                        ""
                     ],
                     "policyDefinitionReferenceId":"",
                     "policyDefinitionId":"/providers/microsoft.authorization/policydefinitions/<policy_def_id>",
                     "effect":"auditifnotexists",
                     "results":{
                        "queryResultsUri":"https://management.azure.com/subscriptions/<subscription_id>/providers/Microsoft.Authorization/policyAssignments/<policy_assignment_id>/providers/Microsoft.PolicyInsights/policyStates/latest/queryResults?api-version=2019-10-01&$from=2020-02-05 12:27:27Z&$to=2020-02-06 12:27:27Z and PolicyAssignmentId eq '/subscriptions/3a8b6402-45a2-4b9b-b6f7-73cbe8e507e2/providers/microsoft.authorization/policyassignments/6dd881dee049489888d7e22e' and PolicyDefinitionId eq '/providers/microsoft.authorization/policydefinitions/013e242c-8828-4970-87b3-ab247555486d'",
                        "nonCompliantResources":1,
                        "resourceDetails":[
                           {
                              "complianceState":"noncompliant",
                              "count":1
                           }
                        ],
                        "policyDetails":[
                           {
                              "complianceState":"noncompliant",
                              "count":1
                           }
                        ],
                        "policyGroupDetails":[
                           {
                              "complianceState":"noncompliant",
                              "count":1
                           }
                        ]
                     }
                  }
               ],
               "policyGroups":[
                  {
                     "policyGroupName":"",
                     "results":{
                        "queryResultsUri":"https://management.azure.com/subscriptions/<subscription_id>/providers/Microsoft.Authorization/policyAssignments/<policy_assignment_id>/providers/Microsoft.PolicyInsights/policyStates/latest/queryResults?api-version=2019-10-01&$from=2020-02-05 12:27:27Z&$to=2020-02-06 12:27:27Z and PolicyAssignmentId eq '/subscriptions/3a8b6402-45a2-4b9b-b6f7-73cbe8e507e2/providers/microsoft.authorization/policyassignments/6dd881dee049489888d7e22e' and PolicySetDefinitionId eq '' and '' in PolicyDefinitionGroupNames",
                        "nonCompliantResources":1,
                        "resourceDetails":[
                           {
                              "complianceState":"noncompliant",
                              "count":1
                           }
                        ],
                        "policyDetails":[
                           {
                              "complianceState":"noncompliant",
                              "count":1
                           }
                        ],
                        "policyGroupDetails":[
                           {
                              "complianceState":"noncompliant",
                              "count":1
                           }
                        ]
                     }
                  }
               ]
            }
         ]
      }
   ]
}
"""
