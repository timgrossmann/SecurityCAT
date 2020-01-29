import boto3

client = boto3.client('config')

response = client.start_config_rules_evaluation(
	ConfigRuleNames=[
		'ec2-stopped-instance'
	]
)

print(response)
