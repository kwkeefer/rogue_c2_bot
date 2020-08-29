from bs4 import BeautifulSoup
import requests
import os
import boto3
from datetime import datetime
import dateutil.parser

SNS_ARN = os.environ['SNS']
DDB_TABLE = os.environ['DYNAMODB']


class Ddb:
    def __init__(self, boto3_session, table_name):
        self.table = boto3_session.resource('dynamodb').Table(table_name)

    def get_item(self, primary_key):
        """"
        Gets a single record in the table
        :param primary_key:
        """
        response = self.table.get_item(
            Key={'check': primary_key}
        )
        if response.get('Item'):
            return response['Item']
        else:
            print(f"{primary_key} does not exist.")

    def update_item(self, primary_key):
        """
        Updates the record with a timestamp
        :param primary_key:
        :return:
        """
        item = {'check': primary_key, "timestamp": datetime.utcnow().isoformat()}
        response = self.table.put_item(
            Item=item,
            ReturnValues='ALL_OLD'
        )
        if item != response.get('Attributes'):
            print(f"Successfully updated {primary_key}.")
        return response


def lambda_handler(event, context):
    """
    :param event:
    :param context:
    :return: None
    """
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    r = requests.get("https://www.roguefitness.com/black-concept-2-model-d-rower-pm5", headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')

    def publish_message(session):
        print("Sending message to SNS topic!")
        client = session.client('sns')
        client.publish(
            TopicArn=SNS_ARN,
            Subject="ROGUE ALERT!  Concept2 in stock!",
            Message="https://www.roguefitness.com/black-concept-2-model-d-rower-pm5"
        )

    print("Checking to see if product is available.")
    if "notified when this product is available" not in str(soup.find(class_='options-container-big')):
        print("Product is available!")
        session = boto3.session.Session()
        table = Ddb(session, DDB_TABLE)
        check = table.get_item("check")
        if not check:
            table.update_item("check")
            publish_message(session)
            print(r.text)
        else:
            now = datetime.now()
            sns_message_last_sent = dateutil.parser.parse(check['timestamp'])
            time_delta = (now - sns_message_last_sent).total_seconds()
            if time_delta > 3600:
                print(f"Last message sent {time_delta} seconds ago.")
                publish_message(session)
                print(r.text)
                table.update_item("check")
            else:
                print(f"Not sending message.  Last message sent {time_delta} seconds ago.")
    else:
        print("Product not available.")
