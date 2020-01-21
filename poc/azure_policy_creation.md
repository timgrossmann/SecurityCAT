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
    "displayName": "[EISA-ACC-201.5] - Audit Windows VMs that do not have a maximum password age of 180 days",
    "policyType": "Custom",
    "mode": "All",
    "description": "This policy audits Windows virtual machines that do not have a maximum password age of 180 days. This policy should only be used along with its corresponding deploy policy in an initiative/policy set.",
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
      "displayName":"[EISA-OPS-401] - Audit diagnostic setting",
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

## Trigger a policy of a Mgmt-Group

```bash
POST https://management.azure.com/providers/Microsoft.Management/managementGroups/mgmt-test/providers/Microsoft.PolicyInsights/policyStates/latest/triggerEvaluation?api-version=2019-10-01&%24filter=%22policyAssimentID%20eq%20%27%2Fproviders%2FMicrosoft.Management%2FmanagementGroups%2Fmgmt-test%2Fproviders%2FMicrosoft.Authorization%2FpolicyAssignments%2F%5BEISA-OPS-401%5D%22
Authorization: Bearer ...{JWT Format}
Content-type: application/json
```

> JWT  eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6InBpVmxsb1FEU01LeGgxbTJ5Z3FHU1ZkZ0ZwQSIsImtpZCI6InBpVmxsb1FEU01LeGgxbTJ5Z3FHU1ZkZ0ZwQSJ9.eyJhdWQiOiJodHRwczovL21hbmFnZW1lbnQuY29yZS53aW5kb3dzLm5ldC8iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC83OGVmN2E3Yy0wMDdiLTQ3ZGItYTI2OC0xZDhiYzFmMDgyZGMvIiwiaWF0IjoxNTc5NTIxMTA4LCJuYmYiOjE1Nzk1MjExMDgsImV4cCI6MTU3OTUyNTAwOCwiYWNyIjoiMSIsImFpbyI6IkFVUUF1LzhPQUFBQUo4ZnpkS0JDZkRCSDMvOE5VS01FQW1zZW4ydGF2eXZlb1RVU0xwSEJUVVJGM3NEYWNpcDdFMzRNeURvWkwvb1AySXlhMXpaZVplcGdoNTNXUXpHL2JRPT0iLCJhbHRzZWNpZCI6IjE6bGl2ZS5jb206MDAwM0JGRkQwMDg5RUIyOSIsImFtciI6WyJwd2QiXSwiYXBwaWQiOiI3ZjU5YTc3My0yZWFmLTQyOWMtYTA1OS01MGZjNWJiMjhiNDQiLCJhcHBpZGFjciI6IjIiLCJlbWFpbCI6ImNvbnRhY3QudGltZ3Jvc3NtYW5uQGdtYWlsLmNvbSIsImZhbWlseV9uYW1lIjoiR3Jvw59tYW5uIiwiZ2l2ZW5fbmFtZSI6IlRpbSIsImdyb3VwcyI6WyJjMDgyMmYyOS1iNDEwLTQxYzEtYjFhNC0wMDFhNjU2NDEwZmQiXSwiaWRwIjoibGl2ZS5jb20iLCJpcGFkZHIiOiIxMzkuMTUuOTguMTMyIiwibmFtZSI6IlRpbSBHcm_Dn21hbm4iLCJvaWQiOiJiMjJjYjgyYy0wNDk2LTRiMjgtOWYwZS1mNzAxZjZjZGU3MmQiLCJwdWlkIjoiMTAwMzIwMDA5NTdBMkNCOCIsInNjcCI6InVzZXJfaW1wZXJzb25hdGlvbiIsInN1YiI6IlNFUlZyTzRsMzk1a0lmTENfalRmLXMwU0tLel9yczFmb25aY2Y2M1I3TUkiLCJ0aWQiOiI3OGVmN2E3Yy0wMDdiLTQ3ZGItYTI2OC0xZDhiYzFmMDgyZGMiLCJ1bmlxdWVfbmFtZSI6ImxpdmUuY29tI2NvbnRhY3QudGltZ3Jvc3NtYW5uQGdtYWlsLmNvbSIsInV0aSI6IllEV2pHcFlpZmtDN05BcDFUMGczQUEiLCJ2ZXIiOiIxLjAiLCJ3aWRzIjpbIjYyZTkwMzk0LTY5ZjUtNDIzNy05MTkwLTAxMjE3NzE0NWUxMCJdfQ.eEpFPAjBVsAZh71PAZtAWnpskzc-V_fJaN12ssCqd2dHB4FIaZpP62uVEWLdmwY5n7zecn2SFDGd9cCiGDAxj46dKs0w_R1rLTNoWuHVOAM7Ox4MD45oPp-JNmZfuGyDxtwOetJ4fZuLYjeRrhwWyvMLXiRY_FtJNaKs48IGNDF37Hrt7VLfXn_-3ioe1i5JiZCpRvHbQOhEJmZlJ5UC66tFOA0UOJMg4nTguwznOj_DEwHtVV1nETzLq-hWKqQaU1JjCEvpDfy7pdqkrPWGySpHfNv7u4mWbloyGBEINRXNuZiUVtaslaeS8mpgC8fV7ckZHmZrnXGiIC_xKtG9wQ