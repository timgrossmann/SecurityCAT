import logging
from threading import Thread

from azure_interactor import AzureInteractor


# setup logging to console and log file
logging.basicConfig(
    format="%(asctime)-8s - %(levelname)-8s: %(message)-8s",
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(), logging.FileHandler("debug.log")],
)


class EvaluationWorker(Thread):
    def __init__(
        self,
        running_evaluations,
        eval_id,
        tenant_id,
        subscription_id,
        client_id,
        client_secret,
        resource,
        policy_id,
        policy_json,
        assignment_id,
    ):
        Thread.__init__(self)

        self.logger = logging.getLogger(__name__)

        self.running_evaluations = running_evaluations
        self.eval_id = eval_id
        self.tenant_id = tenant_id
        self.subscription_id = subscription_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.resource = resource
        self.policy_id = policy_id
        self.policy_json = policy_json
        self.assignment_id = assignment_id

        self.output_res = {
            "id": eval_id,
            "result": {"message": f"", "status": "ERROR", "confidenceLevel": "0",},
        }

        self.interactor = self.__authenticate()

    def run(self):

        # Try to create a policy definition
        try:
            is_def_created = self.__create_policy_def()

            if not is_def_created:
                return
        except Exception as err:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"Policy definition {policy_id} could not be created - {err}..."

            self.running_evaluations[eval_id] = self.output_res

        # Try to assign the policy definition
        try:
            is_assign_created = __assign_policy_def()

            if not is_def_created:
                return
        except Exception as err:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"Policy assignment {self.assignment_id} could not be created - {err}"

            self.running_evaluations[eval_id] = self.output_res

        # Try to trigger the policy assignment

    def __authenticate(self):
        """Tries to authenticate and get an access token
        
        Returns:
        AzureInteractor object: containing the session with Azure
        """

        self.logger.info(f"Authenticating service principal with {self.client_id}")
        interactor = AzureInteractor(
            self.tenant_id, self.subscription_id, self.client_id, self.client_secret
        )

        return interactor

    def __create_policy_def(self):
        """Tries to create a policy definition with the given policy json
        
        Returns:
        bool: True if policy was created successfully, false if not
        """

        self.logger.info(f"Creating policy definition {self.policy_id}")
        policy_definition_res = self.interactor.put_policy_definition(
            self.policy_id, self.policy_json
        )

        # definition was not created, report and abort
        if policy_definition_res.status_code != 201:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"Policy definition {self.policy_id} could not be created - {policy_definition_res.status_code}: {policy_definition_res.text}"

            self.running_evaluations[eval_id] = self.output_res
            return False

        return True

    def __assign_policy_def(self):
        """Tries to assign the policy definition to the assignment_id
        
        Returns:
        bool: True if policy was assigned successfully, false if not
        """

        self.logger.info(
            f"Creating policy assignment of definition {self.olicy_id} to assignment {self.assignment_id}"
        )
        policy_assignment_res = self.interactor.put_policy_assignment(
            self.policy_id, self.assignment_id
        )

        if policy_assignment_res.status_code != 201:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"Policy assignment {self.assignment_id} could not be created - {policy_assignment_res.status_code}: {policy_assignment_res.text}"

            self.running_evaluations[eval_id] = self.output_res
            return False

        return True

    def __trigger_policy(self):
        self.logger.info(f"Triggering created policy assignment {assignment_id}")
        eval_status_loc = self.interactor.trigger_policy().headers["location"]
        self.logger.debug(f"Policy evaluation for {assignment_id} at {eval_status_loc}")

        self.logger.debug(
            f"Starting poll cycle for {assignment_id}. Polling {eval_status_loc}"
        )
        self.interactor.wait_for_eval_complete(check_loc)

        # TODO get summary for evaluation here
