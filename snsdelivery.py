import boto3
import json
from botocore.exceptions import ClientError
import os, sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/venv3/lib/python3.6/site-packages/")
import requests

SNS_ARN = os.environ['SNS_ARN']
MAX_PER_SECOND = os.environ['MAX_PER_SECOND']

def main(event, context):
    delivery_policy = {
        "http": {
            "defaultHealthyRetryPolicy": {
                "minDelayTarget": 20,
                "maxDelayTarget": 20,
                "numRetries": 3,
                "numMaxDelayRetries": 0,
                "numNoDelayRetries": 0,
                "numMinDelayRetries": 0,
                "backoffFunction": "linear"
            },
            "disableSubscriptionOverrides": False,
            "defaultThrottlePolicy": {
                "maxReceivesPerSecond": int(MAX_PER_SECOND)
            }
        }
    }

    if event['RequestType'] in ['Create', 'Update']:
        sns = boto3.client('sns')
        try:
            response = sns.set_topic_attributes(
                TopicArn=SNS_ARN,
                AttributeName='DeliveryPolicy',
                AttributeValue=json.dumps(delivery_policy)
            )
            sendResponse(event, '', 'SUCCESS')
        except ClientError as e:
            print('Problem setting delivery policy: {}'.format(e))
            sendResponse(event, str(e), 'FAILED')
    else:
        sendResponse(event, '', 'SUCCESS')

def sendResponse(event, reason, status):
    response = {
        'Status': status,
        'Reason': reason,
        'PhysicalResourceId': 'physical-resource-id',
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId']
    }
    print(response)
    try:
        cfn_response = requests.put(event['ResponseURL'], data=json.dumps(response))
        print(cfn_response.status_code, cfn_response.text)
    except requests.exceptions.RequestException as e:
        print('Problem connecting to CloudFormation: {}'.format(e))
    return
