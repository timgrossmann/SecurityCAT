#!/usr/bin/env python3
import logging
import json
import multiprocessing
import uuid

import requests
from flask import Flask, request, jsonify
from flask_restplus import Resource, Api, fields, reqparse

from azure_interactor import AzureInteractor


# setup logging to console and log file
logging.basicConfig(
    format="%(asctime)-8s - %(levelname)-8s: %(message)-8s",
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(), logging.FileHandler("debug.log")],
)

app = Flask(__name__)
api = Api(app)

# dict holding the currently running evaluations
running_evaluations = {}

# Parameters given for a start of a policy evaluation
policy_eval_definition = api.model(
    "PolicyEvalDefinition",
    {
        "tenantId": fields.String(
            description="Tenant-id from Azure AD", required=True,
        ),
        "subscriptionId": fields.String(
            description="Subscription_id of azure subscription", required=True,
        ),
        "clientId": fields.String(
            description="Client id from application for service principal",
            required=True,
        ),
        "clientSecret": fields.String(
            description="Client secret from application for service principal",
            required=True,
        ),
        "resource": fields.String(
            description="Optional url endpoint of azure resource ([default] 'https://management.azure.com/')",
            required=False,
        ),
        "policyId": fields.String(
            description="Unique identifier for policy definition", required=True,
        ),
        "policyJson": fields.String(
            description="Stringified json of the policy definition in the format of https://docs.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure",
            required=True,
        ),
        "assignmentId": fields.String(
            description="Optional unique identifier for policy assignment (policyId will be used if not given)",
            required=False,
        ),
    },
)

# Policy evaluation result structure expected by SecurityRAT
policy_eval_result = api.model(
    "PolicyEvalResultStructure",
    {
        "id": fields.String(description="Unique id of the "),
        "result": fields.Nested(
            api.model(
                "PolicyEvalResult",
                {
                    "status": fields.String(
                        description="Requirement fulfilled? (PASSED/FAILED/ERROR/IN_PROGRESS)"
                    ),
                    "confidenceLevel": fields.Integer(description="Value in percent"),
                    "message": fields.String(description="Result message"),
                },
            )
        ),
    },
)


def get_error_res(eval_id):
    """Creates a default error response based on the policy_evaluation_result structure
    
    Parameters:
    eval_id (String): Unique identifier for evaluation policy
    
    Returns:
    PolicyEvalResultStructure object: with the error state with the given id
    """
    return {
        "id": eval_id,
        "result": {
            "message": f"No evaluation with the id {eval_id} ongoing",
            "status": "ERROR",
            "confidenceLevel": "0",
        },
    }


def process_policy_evaluation(
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
    """Creates a default error response based on the policy_evaluation_result structure
    
    Parameters:
    eval_id (String): Unique identifier for evaluation policy
    """

    try:
        app.logger.info(f"Authenticating service principal with {client_id}")
        interactor = AzureInteractor(tenant_id, subscription_id, client_id, client_secret)

    except Exception as err:
        app.logger.info(f"Could not authenticate to Azure with given credentials for client {client_id}")
        
        output_res["result"]["status"] = "ERROR"
        output_res["result"][
            "message"
        ] = f"Could not authenticate to Azure with given credentials for client {client_id}"

        running_evaluations[eval_id] = output_res
        return
    
    
    app.logger.info(f"Creating policy definition {policy_id}")
    policy_definition_res = interactor.put_policy_definition(policy_id, policy_json)

    # definition was not created, report and abort
    if policy_definition_res.status_code != 201:
        output_res["result"]["status"] = "ERROR"
        output_res["result"][
            "message"
        ] = f"Policy definition {policy_id} could not be created - {policy_definition_res.status_code}: {policy_definition_res.text}"

        running_evaluations[eval_id] = output_res
        return output_res

    app.logger.info(
        f"Creating policy assignment of definition {policy_id} to assignment {assignment_id}"
    )
    policy_assignment_res = interactor.put_policy_assignment(policy_id, assignment_id)

    if policy_assignment_res.status_code != 201:
        output_res["result"]["status"] = "ERROR"
        output_res["result"][
            "message"
        ] = f"Policy assignment {assignment_id} could not be created - {policy_assignment_res.status_code}: {policy_assignment_res.text}"

        running_evaluations[eval_id] = output_res
        return output_res

    app.logger.info(f"Triggering created policy assignment {assignment_id}")
    eval_status_loc = interactor.trigger_policy().headers["location"]
    app.logger.debug(f"Policy evaluation for {assignment_id} at {eval_status_loc}")

    app.logger.debug(
        f"Starting poll cycle for {assignment_id}. Polling {eval_status_loc}"
    )
    interactor.wait_for_eval_complete(check_loc)

    # TODO get summary for evaluation here


### Policy evaluation status check
@api.route("/api/tests/<test_id>", methods=["GET"])
class PolicyResult(Resource):
    @api.doc(responses={200: "Test result"})
    @api.marshal_list_with(policy_eval_result)
    def get(self, test_id):
        eval_state = running_evaluations.get(test_id)

        if not eval_state:
            return get_error_res(test_id)

        return eval_state


### Policy evaluation class
@api.route("/api/tests", methods=["POST"])
class PolicyEvaluation(Resource):
    @api.doc(responses={200: "Test result"})
    @api.expect(policy_eval_definition)
    @api.marshal_list_with(policy_eval_result)
    def post(self):
        request_params = api.payload

        eval_id = str(uuid.uuid4())
        tenant_id = request_params["tenantId"]
        subscription_id = request_params["subscriptionId"]
        client_id = request_params["clientId"]
        client_secret = request_params["clientSecret"]
        resource = request_params.get("resource")
        policy_id = request_params["policyId"]
        assignment_id = request_params.get("assignmentId", policy_id)
        policy_json = request_params["policyJson"]

        output_res = {
            "id": eval_id,
            "result": {"message": "None", "status": "FAILED", "confidenceLevel": "0",},
        }

        # if policy definition is string then try parse
        # if not valid, abort
        try:
            if isinstance(policy_json, str):
                app.logger.debug("String")
                policy_json = json.loads(policy_json)
        except ValueError:
            app.logger.error(f"Error decoding given policy json - {policy_json}")
            output_res["result"][
                "message"
            ] = f"Error decoding given policy json - {policy_json}"
            output_res["result"]["status"] = "ERROR"

            return output_res

        output_res["result"]["status"] = "IN_PROGRESS"
        running_evaluations[eval_id] = output_res

        thread = multiprocessing.Process(
            target=process_policy_evaluation,
            args=(
                eval_id,
                tenant_id,
                subscription_id,
                client_id,
                client_secret,
                resource,
                policy_id,
                policy_json,
                assignment_id,
            ),
        )
        thread.start()

        return output_res


if __name__ == "__main__":
    app.run(debug=True, port=5000)  # threaded=True by default
