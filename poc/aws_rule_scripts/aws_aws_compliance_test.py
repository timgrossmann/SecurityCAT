# Needs ~/.aws/config & ~/.aws/credentials
#
# .aws/config
# [default]
# region=us-east-1
#
# ./aws/credentials
# [default]
# aws_access_key_id = <access_key>
# aws_secret_access_key = <access-secret>
#

import boto3

client = boto3.client("config")

response = client.get_compliance_details_by_config_rule(
    ConfigRuleName="ec2-stopped-instance"
)

print(response)
