import boto3
from botocore.config import Config

boto3.set_stream_logger('create')

client = boto3.client('config', config=Config(proxies={'http': 'http://localhost:3128', 'https': 'http://localhost:3128'}))
response = client.put_config_rule(
    ConfigRule={
        'Source': {
            'ConfigRuleName': 'ec2-stopped-instance'
            'Owner': 'AWS',
            'SourceIdentifier': 'EC2_STOPPED_INSTANCE',
        }
    }
)

