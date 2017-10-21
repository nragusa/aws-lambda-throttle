import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/venv3/lib/python3.6/site-packages/')
import requests

TABLE_NAME = os.environ['TABLE_NAME']

def main(event, context):
    event = json.loads(event['body'])
    print(event)
    try:
        if event['Type'] == 'SubscriptionConfirmation':
            print('Received request to subscribe to SNS')
            try:
                confirm = requests.get(event['SubscribeURL'])
                print('Subscription status: {}'.format(confirm.status_code))
            except requests.exceptions.RequestException as e:
                print('Problem subscribing to SNS: {}'.format(str(e)))
            return
        else:
            message = json.loads(event['Message'])
            print('Message: {}'.format(message['Records']))
            my_key = message['Records'][0]['s3']['object']['key']
    except KeyError:
        print('Key not found in dictionary')
    ddb = boto3.resource('dynamodb')
    table = ddb.Table(TABLE_NAME)
    try:
        response = table.put_item(
            Item={
                'myid': my_key,
                'now': datetime.now().isoformat(' ')
            }
        )
        return {'statusCode': 200, 'body': json.dumps({'status': 'ok'})}
    except ClientError as e:
        print('Error adding item to DDB: {}'.format(e))
        return {'statusCode': 400, 'body': json.dumps({'status': str(e)})}
