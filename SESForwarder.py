from email import message_from_file
import json
import re
import boto3


bucketConfig        = "s3-testing-bucket-testing-ew1"
bucketKeyConfig     = "pythonConfig/defaultConfig.json"

# This is a back up configuration file
# In case there is a problem accessing the object in the s3 bucket
defaultConfigBackUp = {
    'original_from'         : '', #The original sender of the email
    'subjectPrefixTemplate' : "[AWS __ACCOUNT_NAME__]",
    'subjectPrefix'         : '',
    'recipientName'         : '', #The name of the recipient without the domain
    'previousSubj'          : '',  #The original subject of the email
    'Verified_From_Email'   : 'test@test.from.com',
    'Ses_Incoming_Bucket'   : "s3-testing-bucket-testing-ew1",
    'prefix'                : 's3prefix/', #the name of the folder inside the bucket

    'Forward_bySender_Mapping' : {
        'aws-example-email-replies@example.com' :[
            ],
    },

    'Forward_byRecipient_Mapping' : {
        "noreply@aws.example.com" : [
        ],
        "@example.com" : [
            'example1.email@example.com',
            'example2.email@example.com'
        ],
    },
}
def lambda_handler(event,context):
    s3     = boto3.client('s3')
    ses    = boto3.client('ses')

    try:
        o2 = s3.get_object(Bucket = bucketConfig,
                            Key = bucketKeyConfig)
        defaultConfig = json.loads(o2['Body'].read())
    except:
        print "There was an error accessing the default Config in s3"
        defaultConfig = defaultConfigBackUp

    record = event['Records'][0]
    assert record['eventSource'] == 'aws:ses'

    o = s3.get_object(Bucket = defaultConfig['Ses_Incoming_Bucket'],
              Key=defaultConfig['prefix'] + record['ses']['mail']['messageId'])

    raw_mail = o['Body']
    recipients = []
    msg = message_from_file(raw_mail)

    del msg['DKIM-Signature']
    del msg['Sender']
    sender = msg['Return-Path'][1:-1]
    del msg['Return-Path']

    defaultConfig['original_from'] = msg['From']
    defaultConfig['previousSubj']  = msg['Subject']

    del msg['Subject']
    del msg['From']
    msg['From'] = (re.sub(r'\<.+?\>', '',
                                    defaultConfig['original_from']).strip() +
                          ' <{}>'.format(defaultConfig['Verified_From_Email']))

    msg['Return-Path'] = defaultConfig['Verified_From_Email']
    recipient = record['ses']['receipt']['recipients'][0]

    defaultConfig['recipientName'] = recipient.split('@')[0]
    defaultConfig['subjectPrefix'] = ('[AWS ' + defaultConfig['recipientName'] +
                                            '] ' + defaultConfig['previousSubj'])
    msg['Subject'] = defaultConfig['subjectPrefix']
    msg_string = msg.as_string()

    for key, value in defaultConfig['Forward_bySender_Mapping'].iteritems():
        print sender
        if key == sender:
            recipients = value
            sendEmail(recipients, msg_string, ses)
            return

    for key, value in defaultConfig['Forward_byRecipient_Mapping'].iteritems():
        if key == recipient:
            recipients = value
            sendEmail(recipients, msg_string, ses)
            return
        if recipient.endswith(key):
            recipients = defaultConfig['Forward_byRecipient_Mapping'].get(key, [])
            sendEmail(recipients, msg_string, ses)
            return
    return

def sendEmail(recipients, msg_string , ses):

    if not recipients:
            print(recipient,
            'Recipent is not found in forwarding map. Skipping recipient.')
    else:
        for address in recipients:
            try:
                ses.send_raw_email(Destinations=[address],
                RawMessage=dict(Data=msg_string))
                return
            except: ('Client error while forwarding email or the recipient list was empty')
