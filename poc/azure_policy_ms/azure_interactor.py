import logging
import re

import requests
from adal import AuthenticationContext


# setup logging to console and log file
logging.basicConfig(
    format="%(asctime)-8s - %(levelname)-8s: %(message)-8s",
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(), logging.FileHandler("debug.log")],
)

logger = logging.getLogger(__file__)


class AzureInteractor:
    def __init__(
        self,
        tenant_id,
        subscription_id,
        client_id,
        client_secret,
        resource="https://management.azure.com/",
        api_version="2019-09-01",
    ):
        """Wrapper for the azure interactions
        
        Parameters:
        tenant_id (String): tenant_id from Azure AD
        subscription_id (String): subscription_id of azure subscription
        client_id (String): client id from application
        client_secret (String): client secret from application
        resource (String): optional url endpoint of azure resource ([default] 'https://management.azure.com/')
        api_version (String): : optional api version of azure services ([default] '2019-09-01')

        Returns:
        AzureInteractor: instance of this class
        """

        self.auth_context = AuthenticationContext(
            f"https://login.microsoftonline.com/{tenant_id}/"
        )
        self.session = requests.Session()
        logging.debug("Requests session created")

        self.subscription_id = subscription_id
        self.api_version = api_version
        self.credentials = {
            "client_id": client_id,
            "client_secret": client_secret,
            "resource": resource,
        }
        self.__update_auth_token(self.credentials)

    def __update_auth_token(self, credentials):
        """Updates the Authorization header of the requests session with the access token for given credentials
        
        Parameters:
        credentials (dict): dictionary containing the client_id, client_secret, and 'resource'
        """

        token_response = self.auth_context.acquire_token_with_client_credentials(
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            resource=credentials["resource"],
        )

        # add bearer token to the requests session
        self.session.headers.update(
            {"Authorization": "Bearer " + token_response["accessToken"]}
        )

        logging.info("Access Token retrieved and set in the current session")

    def __get_policy_def_endpoint(self, policy_id):
        """Creates the URI for policy definitions with the given policy_id
        
        Parameters:
        policy_id (String): unique identifier for policy definition
        
        Returns:
        String: URI of the definition endpoint filled with the given policy_id
        """

        return f"https://management.azure.com/subscriptions/{self.subscription_id}/providers/Microsoft.Authorization/policyDefinitions/{policy_id}?api-version={self.api_version}"

    def __get_policy_assign_endpoint(self, assignment_id):
        """Creates the URI for policy definitions with the given assignment_id
        
        Parameters:
        assignment_id (String): unique identifier for policy assignment
        
        Returns:
        String: URI of the assignment endpoint filled with the given assignment_id
        """

        return f"https://management.azure.com/subscriptions/{self.subscription_id}/providers/Microsoft.Authorization/policyAssignments/{assignment_id}?api-version={self.api_version}"

    def __get_policy_trigger_endpoint(self):
        """Creates the URI for policy triggering
        
        Returns:
        String: URI of the trigger endpoint
        """

        return f"https://management.azure.com/subscriptions/{self.subscription_id}/providers/Microsoft.PolicyInsights/policyStates/latest/triggerEvaluation?api-version=2019-10-01"

    def __get_policy_summary_endpoint(self, assignment_id):
        """Creates the URI for policy evaluation summary with the given assignment_id
        
        Parameters:
        assignment_id (String): unique identifier for policy assignment
        
        Returns:
        String: URI of the assignment endpoint filled with the given assignment_id
        """

        return f"https://management.azure.com/subscriptions/{self.subscription_id}/providers/Microsoft.Authorization/policyAssignments/{assignment_id}/providers/Microsoft.PolicyInsights/policyStates/latest/summarize?api-version=2019-10-01"

    def __get_url(self, url):
        """Get calls the given url
        Trigger evaluation state for execution (202 if going, 200 if succeeded)
        
        Parameters:
        url (String): url to do the get call to
        
        Returns:
        requests Response object: instance of Response of the get operation
        """

        result = self.session.get(url)
        return result

    def __post_url(self, url):
        """Post calls the given url
        
        Parameters:
        url (String): url to do the get call to
        
        Returns:
        requests Response object: instance of Response of the post operation
        """

        result = self.session.post(url)
        return result
    
    def __delete_url(self, url):
        """Delete calls the given url
        
        Parameters:
        url (String): url to do the get call to
        
        Returns:
        requests Response object: instance of Response of the delete operation
        """
        
        result = self.session.delete(url)
        return result

    def get_policy_definition(self, policy_id):
        """Updates the Authorization header of the requests session with the access token for given credentials
        
        Parameters:
        credentials (dict): dictionary containing the client_id, client_secret, and 'resource'
        
        Returns:
        requests Response object: instance of Response of the get operation
        """

        policy_get_endpoint = self.__get_policy_def_endpoint(policy_id)
        result = self.session.get(policy_get_endpoint)

        return result

    def put_policy_definition(self, policy_id, definition_json):
        """Creates a azure policy definition with the given policy_id and the given json data
        
        Parameters:
        policy_id (String): unique identifier for policy definition
        definition_json (dict): dictionary of the policy definition in the format of https://docs.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure
        
        Returns:
        requests Response object: instance of Response of the put operation
        """
            
        policy_def_endpoint = self.__get_policy_def_endpoint(policy_id)
        result = self.session.put(policy_def_endpoint, json=definition_json)

        logging.info(
            f"Creating Policy definition with id {policy_id} in subscription {self.subscription_id}"
        )

        return result

    def put_policy_assignment(self, assignment_id, policy_id):
        """Creates a azure policy assignment with the given assignment_id and policy_id
        
        Parameters:
        assignment_id (String): unique identifier for policy assignment
        policy_id (String): unique identifier for policy definition
        
        Returns:
        requests Response object: instance of Response of the put operation
        """

        policy_def = self.get_policy_definition(policy_id)

        try:
            policy_def_json = policy_def.json()

            data = {
                "properties": {
                    "displayName": policy_def_json["properties"]["displayName"],
                    "description": policy_def_json["properties"]["description"],
                    "metadata": {"assignedBy": "Azure Interactor Script"},
                    "policyDefinitionId": policy_def_json["id"],
                    "enforcementMode": "Default",
                    "parameters": {},
                }
            }

            policy_assign_endpoint = self.__get_policy_assign_endpoint(assignment_id)
            result = self.session.put(policy_assign_endpoint, json=data)

            logging.info(
                f"Creating Policy assignment with id {policy_id} ({policy_def_json['properties']['displayName']}) in subscription {self.subscription_id}"
            )

            return result

        except Exception as err:
            logging.error(f"Could not get policy with id {policy_id} - {err}")
            raise err

    def trigger_policy(self, assignment_id=None):
        """Triggers the evaluation of the policies in scope. If assignment_id given, only triggers the policies of the assignment
        https://docs.microsoft.com/en-us/azure/governance/policy/how-to/get-compliance-data#on-demand-evaluation-scan
        
        Parameters:
        assignment_id (String): unique identifier for policy assignment
        
        Returns:
        requests Response object: instance of Response of the put operation (trigger evaluation, get back url to check evaluation state)
        """

        data = {}

        # TODO find solution to fix filtering
        if assignment_id:
            data = {
                "$filter": "PolicyAssignmentId eq '/subscriptions/{self.subscription_id}/providers/Microsoft.Authorization/policyAssignments/{assignment_id}/'"
            }

        trigger_endpoint = self.__get_policy_trigger_endpoint()
        result = self.session.post(trigger_endpoint, json=data)

        # replace the api-version given by the request with the only one currently supported , '2018-07-01-preview'
        result.headers["location"] = re.sub(
            r"(api-version=)(.*)",
            r"\g<1>2018-07-01-preview",
            result.headers["location"],
            flags=re.IGNORECASE,
        )
        logging.debug(f"Status URI of trigger request: {result.headers['location']}")

        return result

    def get_policy_eval_state(self, eval_url):
        """Requests the policy evaluation state of the given url
        (Status Code 202 - Pending, 200 - Completed)
        
        Parameters:
        eval_url (String): url returned by the trigger policy evaluation  call
        
        Returns:
        requests Response object: instance of Response of the policy evaluation
        """

        return self.__get_url(eval_url)

    def get_policy_eval_summary(self, assignment_id):
        """Requests the policy evaluation state of the given url
        
        Parameters:
        assignment_id (String): unique identifier for policy assignment
        
        Returns:
        requests Response object: instance of Response of the policy evaluation
        """

        evaluation_summary_url = self.__get_policy_summary_endpoint(assignment_id)
        return self.__post_url(evaluation_summary_url)

    def delete_policy_definition(self, policy_id):
        """Delete the policy defintion of the given policy
        
        Parameters:
        policy_id (String): unique identifier for policy definition
        
        Returns:
        requests Response object: instance of Response of the policy definition deletion
        """
        
        delete_definition_url = self.__get_policy_def_endpoint(policy_id)
        return self.__delete_url(delete_definition_url)
    
    def delete_policy_assignment(self, assignment_id):
        """Delete the policy assignment of the assignment_id
        
        Parameters:
        assignment_id (String): unique identifier for policy assignment
        
        Returns:
        requests Response object: instance of Response of the policy definition deletion
        """
        
        delete_assignment_url = self.__get_policy_assign_endpoint(assignment_id)
        return self.__delete_url(delete_assignment_url)
