import boto3

client = boto3.client('config')

response = client.put_config_rule(
	ConfigRule={
		'ConfigRuleName': 'ec2-stopped-instance',
		'Source': {
			'Owner': 'AWS',
			'SourceIdentifier': 'EC2_STOPPED_INSTANCE',
		},
		'InputParameters': '{"AllowedDays":"30"}'
	}
)

print(response)
