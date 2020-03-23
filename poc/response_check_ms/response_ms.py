#!/usr/bin/env python3
import logging
import json
import uuid

import requests
from flask import Flask, request, jsonify
from flask_restplus import Resource, Api, fields, reqparse

from response_ms_thread import EvaluationWorker


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

# Parameters given for a start of a response evaluation
response_eval_definition = api.model(
    "ResponseEvalDefinition",
    {
        # TODO adjust definition to dict and not only string containing short name
        "requirement": fields.String(
            description="To be tested requirement", required=True,
        ),
        "appUrl": fields.String(
            description="Url of the to be tested application", required=True,
        ),
    },
)

# Response evaluation result structure expected by SecurityRAT
response_eval_result = api.model(
    "ResponseEvalResultStructure",
    {
        "id": fields.String(description="Unique id of the "),
        "result": fields.Nested(
            api.model(
                "ResponseEvalResult",
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
    """Creates a default error response based on the response_evaluation_result structure
    
    Parameters:
    eval_id (String): Unique identifier for evaluation
    
    Returns:
    ResponseEvalResultStructure object: with the error state with the given id
    """
    return {
        "id": eval_id,
        "result": {
            "message": f"No evaluation with the id {eval_id} ongoing",
            "status": "ERROR",
            "confidenceLevel": "0",
        },
    }


### Response evaluation status check
@api.route("/api/tests/<test_id>", methods=["GET"])
class EvaluationResult(Resource):
    @api.doc(responses={200: "Test result"})
    @api.marshal_list_with(response_eval_result)
    def get(self, test_id):
        eval_state = running_evaluations.get(test_id)

        if not eval_state:
            return get_error_res(test_id)

        return eval_state


### Response evaluation class
@api.route("/api/tests", methods=["POST"])
class Evaluation(Resource):
    @api.doc(responses={200: "Test result"})
    @api.expect(response_eval_definition)
    @api.marshal_list_with(response_eval_result)
    def post(self):
        request_params = api.payload

        eval_id = str(uuid.uuid4())
        requirement = request_params["requirement"]
        app_url = request_params["appUrl"]

        output_res = {
            "id": eval_id,
            "result": {
                "message": "None",
                "status": "IN_PROGRESS",
                "confidenceLevel": "0",
            },
        }
        running_evaluations[eval_id] = output_res

        # TODO replace with worker pool with queue to avoid spawning hundreds of threads
        try:
            app.logger.info(
                f"Starting response evaluation worker thread for eval_id {eval_id}"
            )

            worker = EvaluationWorker(
                running_evaluations, eval_id, requirement, app_url,
            )
            # daemon will let main thread exit even though workers blocking
            worker.daemon = True
            worker.start()
        except Exception as err:
            app.logger.info(
                f"Could not create response evalution worker thread for eval_id {eval_id}... {err}"
            )

            output_res["result"]["status"] = "ERROR"
            output_res["result"][
                "message"
            ] = f"Could not create response evalution worker thread for eval_id {eval_id}... {err}"

            running_evaluations[eval_id] = output_res

        return output_res


if __name__ == "__main__":
    app.run(debug=True, port=5000)
