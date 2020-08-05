## Policy Definition
> https://docs.microsoft.com/en-us/rest/api/resources/policydefinitions/createorupdateatmanagementgroup

```bash
PUT https://management.azure.com/providers/Microsoft.Management/managementgroups/mgmt-test/providers/Microsoft.Authorization/policyDefinitions/%7BpolicyDefinitionName%7D?api-version=2019-09-01
Authorization: Bearer ...{JWT Format}
Content-type: application/json
````

#### JSON Body
```json
{
  "properties": {
    "displayName": "[MSA-0.0.1] - Audit Windows VMs that do not have a maximum password age of 180 days",
    "policyType": "Custom",
    "mode": "All",
    "description": "This policy audits Windows virtual machines that do not have a maximum password age of 180 days.",
    "metadata": {
      "category": "MSA-OS"
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
            "equals": "MaximumPasswordAge"
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
```

## Policy Assignment

> https://docs.microsoft.com/en-us/rest/api/resources/policyassignments/create

```bash
PUT https://management.azure.com/%2Fproviders%2FMicrosoft.Management%2FmanagementGroups%2Fmgmt-test/providers/Microsoft.Authorization/policyAssignments/%7BpolicyAssignmentName%7D?api-version=2019-09-01
Authorization: Bearer ...{JWT Format}
Content-type: application/json
```

#### JSON Body
```json
{
   "properties":{
      "displayName":"[MSA-0.0.2] - Audit diagnostic setting",
      "description":"",
      "metadata":{
         "assignedBy":"Tim Großmann"  
         },
      "scope":"/providers/Microsoft.Management/managementGroups/mgmt-test",
      "notScopes":[],
      "policyDefinitionId":"/providers/Microsoft.Management/managementgroups/mgmt-test/providers/Microsoft.Authorization/policyDefinitions/{policyDefinitionName}",
      "enforcementMode":"Default",
      "parameters":{}
    }
}
```

## Check assigned policies for Mgmt-Group

> https://docs.microsoft.com/en-us/rest/api/resources/policyassignments/listformanagementgroup

```bash
GET https://management.azure.com/providers/Microsoft.Management/managementgroups/mgmt-test/providers/Microsoft.Authorization/policyAssignments?%24filter=atScope()&api-version=2019-09-01
Authorization: Bearer ...{JWT Format}
```

## Summary for Policy Definition

> https://docs.microsoft.com/en-us/rest/api/policy-insights/policystates/summarizeforpolicydefinition

```bash
POST https://management.azure.com/subscriptions/3a8b6402-45a2-4b9b-b6f7-73cbe8e507e2/providers/Microsoft.Authorization/policyDefinitions/{policyName}/providers/Microsoft.PolicyInsights/policyStates/latest/summarize?api-version=2019-10-01
Authorization: Bearer ...{JWT Format}
Content-type: application/json
```




## Trigger a policy of a Mgmt-Group

```bash
POST https://management.azure.com/providers/Microsoft.Management/managementGroups/mgmt-test/providers/Microsoft.PolicyInsights/policyStates/latest/triggerEvaluation?api-version=2019-10-01&%24filter=%22policyAssimentID%20eq%20%27%2Fproviders%2FMicrosoft.Management%2FmanagementGroups%2Fmgmt-test%2Fproviders%2FMicrosoft.Authorization%2FpolicyAssignments%2F%5BEISA-OPS-401%5D%22
Authorization: Bearer ...{JWT Format}
Content-type: application/json
```


```bash
https://management.azure.com/subscriptions/3a8b6402-45a2-4b9b-b6f7-73cbe8e507e2/providers/Microsoft.Authorization/policyDefinitions/17a70ac088d1422abd3e7e3b/providers/Microsoft.PolicyInsights/policyStates/latest/summarize?api-version=2019-10-01

/subscriptions/{subscription-id}/resourceGroups/{RG-Name}/providers/Microsoft.Authorization/policyAssignments/{Policyassignment-id}

/subscriptions/{subscriptionId}/providers/Microsoft.PolicyInsights/policyStates/latest/triggerEvaluation?api-version=2018-07-01-preview

curl -XPOST -H "Authorization: <token>" -H "Content-type: application/json" "https://management.azure.com/subscriptions/<subscription_id>/providers/Microsoft.PolicyInsights/policyStates/latest/triggerEvaluation?api-version=2018-07-01-preview"
```
