import logging
import json
from threading import Thread, get_ident
from time import sleep

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
        self.logger.debug(f"EvaluationWorker created - {get_ident()}")

        self.sleep_time = 60

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
            "id": self.eval_id,
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
            ] = f"Policy definition {self.policy_id} could not be created - {err}..."

            self.running_evaluations[self.eval_id] = self.output_res
            return

        # Try to assign the policy definition
        try:
            is_assign_created = self.__assign_policy_def()

            if not is_assign_created:
                return
        except Exception as err:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"Policy assignment {self.assignment_id} could not be created - {err}"

            self.running_evaluations[self.eval_id] = self.output_res
            return

        # Try to trigger the policy assignment
        eval_state_url = ""
        try:
            eval_state_url = self.__trigger_policy()
        except Exception as err:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"Could not trigger evaluation of assignment with id {self.assignment_id} - {err}"

            self.running_evaluations[self.eval_id] = self.output_res
            return

        # Wait for the evaluation to be complete
        try:
            self.__poll_evalutation_result(eval_state_url, self.sleep_time)
        except Exception as err:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"Could not poll result of evaluation for {eval_state_url} - {err}"

            self.running_evaluations[self.eval_id] = self.output_res
            return

        # Get final summary and update the running_evaluations entry for this eval_id
        try:
            evaluation_result = self.__get_evaluation_summary()

            self.output_res["result"]["status"] = (
                "FAILED"
                if evaluation_result["nonCompliantResources"] > 0
                else "SUCCESS"
            )
            self.output_res["result"]["message"] = json.dumps(
                evaluation_result, indent=4
            )

            self.running_evaluations[self.eval_id] = self.output_res
            return

        except Exception as err:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"Could not get result of evaluation for {self.eval_id} - {err}"

            self.running_evaluations[self.eval_id] = self.output_res
            return

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

            self.running_evaluations[self.eval_id] = self.output_res
            return False

        return True

    def __assign_policy_def(self):
        """Tries to assign the policy definition to the assignment_id
        
        Returns:
        bool: True if policy was assigned successfully, false if not
        """

        self.logger.info(
            f"Creating policy assignment of definition {self.policy_id} to assignment {self.assignment_id}"
        )
        policy_assignment_res = self.interactor.put_policy_assignment(
            self.policy_id, self.assignment_id
        )

        if policy_assignment_res.status_code != 201:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"Policy assignment {self.assignment_id} could not be created - {policy_assignment_res.status_code}: {policy_assignment_res.text}"

            self.running_evaluations[self.eval_id] = self.output_res
            return False

        return True

    def __trigger_policy(self):
        """Tries to trigger the evaluation of the policy with the given assignment_id
        
        Returns:
        String: State url of the triggered policy evaluation
        """

        self.logger.info(f"Triggering policy assignment {self.assignment_id}")
        eval_status_loc = self.interactor.trigger_policy().headers["location"]
        self.logger.debug(
            f"Policy evaluation for {self.assignment_id} at {eval_status_loc}"
        )

        return eval_status_loc

    def __poll_evalutation_result(self, eval_state_url, sleep_time):
        """Waits for the policy evaluation given at the url to be completed,
        blocks while evaluation ongoing
        (Status Code 202 - Pending, 200 - Completed)
        
        Parameters:
        eval_state_url (String): url returned by the trigger policy evaluation  call
        sleep_time (int): interval wait time between checks
        """

        self.logger.debug(
            f"Starting poll cycle for {self.assignment_id}, eval_id {self.eval_id}. Polling {eval_state_url}"
        )

        result = self.interactor.get_policy_eval_state(eval_state_url)

        while result.status_code == 202:
            logging.debug(
                f"Evaluation for eval_id {self.eval_id} still ongoing, waiting {sleep_time} seconds before next check"
            )
            sleep(sleep_time)
            result = self.interactor.get_policy_eval_state(eval_state_url)

        logging.debug(f"Evaluation for eval_id {self.eval_id} done:  {result}")

    def __get_evaluation_summary(self):
        """Tries to get the summary of the just finished evaluation
        
        Returns:
        dict: Containing the evaluation result of the policy assignment
        """
        self.logger.debug(
            f"Getting summary for assignment {self.assignment_id}, eval_id {self.eval_id}"
        )
        result = self.interactor.get_policy_eval_summary(self.assignment_id)

        if result.status_code != 200:
            logging.debug(
                f"Could not get summary for assignment {self.assignment_id} for eval_id {self.eval_id} - {result.text}"
            )
            raise Exception(
                f"Summary could not be retrived: {result.status_code} - {result.text}"
            )

        return result.json()["value"][0]["results"]
