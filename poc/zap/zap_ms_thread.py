import logging
import json
from threading import Thread, get_ident
import time

from requests import exceptions
from zapv2 import ZAPv2

# setup logging to console and log file
logging.basicConfig(
    format="%(asctime)-8s - %(levelname)-8s: %(message)-8s",
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(), logging.FileHandler("debug.log")],
)


class EvaluationWorker(Thread):
    def __init__(
        self, running_evaluations, eval_id, app_url, zap_api_key,
    ):
        self.start_time = time.time()

        Thread.__init__(self)

        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"EvaluationWorker created - {get_ident()}")

        self.sleep_time = 10

        self.running_evaluations = running_evaluations
        self.eval_id = eval_id
        self.app_url = app_url
        self.zap_api_key = zap_api_key

        self.output_res = {
            "id": self.eval_id,
            "result": {
                "message": f"",
                "status": "IN_PROGRESS",
                "confidenceLevel": "0",
            },
        }

        self.session = self.__initiate_zap_session()

    def run(self):
        self.init_time = (time.time() - self.start_time)

        # Try to default spider the app
        try:
            self.__d_spider_app()
            self.d_sider_time = (time.time() - self.start_time) - self.init_time

        except Exception as err:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"App at {self.app_url} could not be spidered with the default spider - {err}..."

            self.running_evaluations[self.eval_id] = self.output_res
            return

        # Try to ajax spider the app
        try:
            self.__a_spider_app()
            self.a_spider_time = (time.time() - self.start_time) - self.init_time - self.d_sider_time

        except Exception as err:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"App at {self.app_url} could not be spidered with ajax - {err}..."

            self.running_evaluations[self.eval_id] = self.output_res
            return

        # Try to active scan the app
        try:
            self.__a_scan_app()
            self.a_scan_time = (time.time() - self.start_time) - self.init_time - self.d_sider_time - self.a_spider_time

        except Exception as err:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"App at {self.app_url} could not be actively scanned (attacked) - {err}..."

            self.running_evaluations[self.eval_id] = self.output_res
            return

        # Try to get the report from ZAP and persist it on disk
        try:
            all_attribute_alerts = self.__get_alert_report()
            alerts = [
                self.__filter_alert_elements(alert) for alert in all_attribute_alerts
            ]
            self.report_time = (time.time() - self.start_time) - self.init_time - self.d_sider_time - self.a_spider_time - self.a_scan_time

            self.output_res["result"] = {
                "message": alerts,
                "status": "PASSED",
                "confidenceLevel": "0",
            }
            self.running_evaluations[self.eval_id] = self.output_res

            self.total_time = (time.time() - self.start_time)

            self.logger.debug(f"""
                Eval_ID:        {self.eval_id}
                Init:           {self.init_time}
                Default Spider: {self.d_sider_time}
                Ajax Spider:    {self.a_spider_time}
                Active Scan:    {self.a_scan_time}
                Report:         {self.report_time}
                Total:          {self.total_time}
            """)

            with open(f'./runs/{self.eval_id}.json', 'w') as out_file:
                out_file.write(json.dumps(alerts, indent=4))

        except Exception as err:
            self.output_res["result"]["status"] = "ERROR"
            self.output_res["result"][
                "message"
            ] = f"Report for app at {self.app_url} could not be retrieved - {err}..."

            self.running_evaluations[self.eval_id] = self.output_res
            return

    def __initiate_zap_session(self):
        """Tries to connect to ZAP and check given api_key
        
        Returns:
        ZAP object: containing the authenticated connection to ZAP
        """
        self.logger.info(f"Connecting to ZAP Proxy Service")
        zap = ZAPv2(apikey=self.zap_api_key)
        zap.spider.scan()

        return zap

    def __d_spider_app(self):
        """Uses the given app_url and scans it with the default spider.
        Returns once the scan is complete
        """

        self.logger.info(f"Spidering target {self.app_url}")
        scanID = self.session.spider.scan(self.app_url)
        while int(self.session.spider.status(scanID)) < 100:
            self.logger.debug(f"Spider progress: {self.session.spider.status(scanID)}%")
            time.sleep(self.sleep_time)

        self.logger.debug(f"Finished spidering {self.app_url} with default spider")

    def __a_spider_app(self, timeout=120):
        """Uses the given app_url and scans it with the default spider.
        Returns once the scan is complete
        
        Parameters:
        timeout (int): number of seconds until the timeout of the ajax spider        
        """

        self.logger.info(f"Spidering target with ajax Spider - {self.app_url}")
        self.session.ajaxSpider.scan(self.app_url)

        timeout_diff = time.time() + timeout
        while self.session.ajaxSpider.status == "running":
            if time.time() > timeout_diff:
                break

            self.logger.debug("Ajax Spider status: " + self.session.ajaxSpider.status)
            time.sleep(self.sleep_time)

        self.logger.info(f"Finished ajax spidering {self.app_url} with ajax spider")

    def __a_scan_app(self):
        """Uses the given app_url and active scans (attacks) it. 
        Returns once the scan is complete
        """

        self.logger.info(f"Active Scanning target {self.app_url}")
        scanID = self.session.ascan.scan(self.app_url)
        while int(self.session.ascan.status(scanID)) < 100:
            self.logger.debug(f"Scan progress: {self.session.ascan.status(scanID)}%")
            time.sleep(self.sleep_time)

        self.logger.info(f"Active Scan completed for {self.app_url}")

    def __get_alert_report(self):
        """Gets the alerts for the given app_url from ZAP 

        Returns:
        dict: JSON containing the triggered alerts of the give app
        """

        self.logger.info(f"Getting alerts for {self.app_url} from ZAP")
        alerts = self.session.core.alerts(baseurl=self.app_url)

        return alerts

    def __filter_alert_elements(self, alert):
        """Removes unused fields from the alert response 

        Returns:
        dict: JSON containing the filtered attributes of an alert
        """

        used_fields = [
            "other",
            "method",
            "evidence",
            "confidence",
            "description",
            "url",
            "reference",
            "solution",
            "alert",
            "risk",
        ]
        new_alert = {}

        for field in used_fields:
            new_alert[field] = alert[field]

        return new_alert

    def __persist_alerts(self, alerts):
        """Writes the given alerts, for the given app_url, to the according file
        for later use.
        """

        self.logger.info(f"Writing alerts for {self.app_url} to file")
        with open(f"./alerts/{self.app_url}", "w") as alert_file:
            self.logger.debug(
                f"Writing alerts for {self.app_url} to ./alerts/{self.app_url}"
            )
            alert_file.write(json.dumps(alerts, indent=4))

        self.logger.info(f"Wrote alerts for {self.app_url} to file")
