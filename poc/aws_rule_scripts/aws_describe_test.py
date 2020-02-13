import boto3

client = boto3.client("config")

response = client.describe_config_rules(ConfigRuleNames=["ec2-stopped-instance"])

print(response)
