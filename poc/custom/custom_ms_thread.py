import logging
import json
from threading import Thread, get_ident
import time

from requests import exceptions

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
        requirement,
        app_url,
    ):
        Thread.__init__(self)

        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"EvaluationWorker created - {get_ident()}")

        self.running_evaluations = running_evaluations
        self.eval_id = eval_id
        self.requirement = requirement
        self.app_url = app_url

        self.output_res = {
            "id": self.eval_id,
            "result": {"message": f"", "status": "IN_PROGRESS", "confidenceLevel": "0",},
        }


    def run(self):
        # Try to request the app_url
        try:
            self.__d_spider_app()

        except Exception as err:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"App at {self.app_url} could not be spidered with the default spider - {err}..."

            self.running_evaluations[self.eval_id] = self.output_res
            return