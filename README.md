# rogue_concept2_bot

This bot checks the Rogue website every three minutes to check whether the Concept2 model D is in stock.
 If it is in stock, a message will be sent to an SNS topic.  The SNS topic can have any number of subscribers configured, so that
 an email will be sent when a message is received.
 
 A maximum of one email per hour will be sent (for every hour that the Concept2 is still in stock).
 
 One can unsubscribe from the SNS topic subscription at any point by clicking the unsubscribe link within each email.
 
 ### Deployment
 Use [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-command-reference.html) to build and deploy this application.
 