import json
import requests

from cred import user, pw

# replace browse with raw in request url
url = 'https://sourcecode.socialcoding.bosch.com/projects/AZURE/repos/azure.bios.repo.template/browse/EISA/Subscription/EISA-INC-101.3/EISA-INC-101.3-AuditSecurityContact.json'

r = requests.get(url, auth=(user, pw))

print(json.loads(r.text))