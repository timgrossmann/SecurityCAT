#!/usr/bin/env python3
import logging
import json
import uuid

import requests
from flask import Flask, request, jsonify
from flask_restplus import Resource, Api, fields, reqparse

from zap_ms_thread import EvaluationWorker


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

# Parameters given for a start of a zap evaluation
zap_eval_definition = api.model(
    "ZapEvalDefinition",
    {
        "appUrl": fields.String(
            description="Url of the to be tested application", required=True,
        ),
        "zapApiKey": fields.String(
            description="API key of the running Zap Instance", required=True,
        ),
    },
)

# ZAP evaluation result structure expected by SecurityRAT
zap_eval_result = api.model(
    "ZapEvalResultStructure",
    {
        "id": fields.String(description="Unique id of the "),
        "result": fields.Nested(
            api.model(
                "ZapEvalResult",
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
    """Creates a default error response based on the zap_evaluation_result structure
    
    Parameters:
    eval_id (String): Unique identifier for zap evaluation
    
    Returns:
    ZapEvalResultStructure object: with the error state with the given id
    """
    return {
        "id": eval_id,
        "result": {
            "message": f"No evaluation with the id {eval_id} ongoing",
            "status": "ERROR",
            "confidenceLevel": "0",
        },
    }


### ZAP evaluation status check
@api.route("/api/tests/<test_id>", methods=["GET"])
class ZapResult(Resource):
    @api.response(200, "Test result", zap_eval_result)
    def get(self, test_id):
        eval_state = running_evaluations.get(test_id)

        if not eval_state:
            return get_error_res(test_id)

        return eval_state


### ZAP evaluation class
@api.route("/api/tests", methods=["POST"])
class ZapEvaluation(Resource):
    @api.expect(zap_eval_definition)
    @api.response(201, "Evaluation created", zap_eval_result)
    def post(self):
        request_params = api.payload

        eval_id = str(uuid.uuid4())
        app_url = request_params["appUrl"]
        zap_api_key = request_params["zapApiKey"]

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
            app.logger.info(f"Starting Zap worker thread for eval_id {eval_id}")

            worker = EvaluationWorker(
                running_evaluations, eval_id, app_url, zap_api_key,
            )
            # daemon will let main thread exit even though workers blocking
            worker.daemon = True
            worker.start()
        except Exception as err:
            app.logger.info(
                f"Could not connect to ZAP proxy with given api token for eval_id {eval_id}... {err}"
            )

            output_res["result"]["status"] = "ERROR"
            output_res["result"][
                "message"
            ] = f"Could not connect to ZAP proxy with given api token for eval_id {eval_id}... {err}"

            running_evaluations[eval_id] = output_res

        return output_res


if __name__ == "__main__":
    app.run(debug=True, port=5000)
