#!/usr/bin/env python3
import logging
import json
import uuid

import requests
from flask import Flask, request, jsonify
from flask_restplus import Resource, Api, fields, reqparse

from azure_ms_thread import EvaluationWorker
from bitbucket_req import get_from_bitbucket


# setup logging to console and log file
logging.basicConfig(
    format="%(asctime)-8s - %(levelname)-8s: %(message)-8s",
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(), logging.FileHandler("debug.log")],
)

app = Flask(__name__)
api = Api(app)

# dict holding the currently running evaluations
# TODO replace with db
running_evaluations = {}

# Parameters given for a start of a policy evaluation
policy_eval_definition = api.model(
    "PolicyEvalDefinition",
    {
        "azure_tenant_id": fields.String(
            description="Tenant-id from Azure AD", required=True,
        ),
        "azure_subscription_id": fields.String(
            description="Subscription_id of azure subscription", required=True,
        ),
        "azure_client_id": fields.String(
            description="Client id from application for service principal",
            required=True,
        ),
        "azure_client_secret": fields.String(
            description="Client secret from application for service principal",
            required=True,
        ),
        "azure_resour": fields.String(
            description="Optional url endpoint of azure resource ([default] 'https://management.azure.com/')",
            required=False,
        ),
        "policy_id": fields.String(
            description="Unique identifier for policy definition", required=True,
        ),
        "policy_json_url": fields.String(
            description="URL of the json policy definition in the format of https://docs.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure",
            required=True,
        ),
        "assignment_id": fields.String(
            description="Optional unique identifier for policy assignment (policy_id will be used if not given)",
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


### Policy evaluation status check
@api.route("/api/tests/<test_id>", methods=["GET"])
class PolicyResult(Resource):
    @api.doc(responses={200: "Test result"})
    @api.marshal_list_with(policy_eval_result)
    def get(self, test_id):
        eval_state = running_evaluations.get(test_id)

        if not eval_state:
            return get_error_res(test_id)

        app.logger.info(eval_state)
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
        tenant_id = request_params["azure_tenant_id"]
        subscription_id = request_params["azure_subscription_id"]
        client_id = request_params["azure_client_id"]
        client_secret = request_params["azure_client_secret"]
        resource = request_params.get("azure_resour")
        policy_id = request_params["policy_id"]
        assignment_id = request_params.get("assignment_id", policy_id)
        policy_json_url = request_params["policy_json_url"]
        policy_json = {}

        output_res = {
            "id": eval_id,
            "result": {"message": "None", "status": "FAILED", "confidenceLevel": "0",},
        }

        try:
            policy_json = get_from_bitbucket(policy_json_url)
            app.logger.debug(f"Retrieved JSON from Socialcoding: {policy_json}")
        except Exception as err:
            app.logger.error(f"Error retrieving policy json - {err}")
            output_res["result"]["message"] = f"Error retrieving policy json - {err}"
            output_res["result"]["status"] = "ERROR"

            return output_res

        output_res["result"]["status"] = "IN_PROGRESS"
        running_evaluations[eval_id] = output_res

        # TODO replace with worker pool with queue to avoid spawning hundreds of threads
        try:
            worker = EvaluationWorker(
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
            )
            # daemon will let main thread exit even though workers blocking
            worker.daemon = True
            worker.start()
        except Exception as err:
            app.logger.info(
                f"Could not authenticate to Azure with given credentials for client {client_id}... {err}"
            )

            output_res["result"]["status"] = "ERROR"
            output_res["result"][
                "message"
            ] = f"Could not authenticate to Azure with given credentials for client {client_id}... {err}"

            running_evaluations[eval_id] = output_res

        return output_res


if __name__ == "__main__":
    app.run(debug=True, port=5000)
