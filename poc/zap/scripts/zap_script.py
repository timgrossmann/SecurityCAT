import time
from pprint import pprint
from zapv2 import ZAPv2

apiKey = "n6odhsffha7clen3tfldunjs0d"
target = "http://localhost:3000/"
zap = ZAPv2(apikey=apiKey)

print("Spidering target {}".format(target))
# The scan returns a scan id to support concurrent scanning
scanID = zap.spider.scan(target)
while int(zap.spider.status(scanID)) < 100:
    # Poll the status until it completes
    print("Spider progress %: {}".format(zap.spider.status(scanID)))
    time.sleep(5)


print("====================================")


print("Ajax Spider target {}".format(target))
scanID = zap.ajaxSpider.scan(target)

timeout = time.time() + 60 * 2  # 2 minutes from now
# Loop until the ajax spider has finished or the timeout has exceeded
while zap.ajaxSpider.status == "running":
    if time.time() > timeout:
        break
    print("Ajax Spider status: " + zap.ajaxSpider.status)
    time.sleep(5)


print("====================================")


# TODO : explore the app (Spider, etc) before using the Active Scan API, Refer the explore section
print("Active Scanning target {}".format(target))
scanID = zap.ascan.scan(target)
while int(zap.ascan.status(scanID)) < 100:
    # Loop until the scanner has finished
    print("Scan progress %: {}".format(zap.ascan.status(scanID)))
    time.sleep(5)

print("Active Scan completed")


print("====================================")


# Print vulnerabilities found by the scanning
print("Hosts: {}".format(", ".join(zap.core.hosts)))
print("Alerts: ")
pprint(zap.core.alerts(baseurl=target))
