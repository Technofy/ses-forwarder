# SES python Forwarder

## Overview

This is a Python2.7 Email forwarder script for AWS Lambda, which uses the AWS SES and S3 services.
Based on : [AWS Lambda SES Email Forwarder](https://github.com/arithmetric/aws-lambda-ses-forwarder)

The forwarder script is using a JSON configuration file which is stored in a s3 bucket.
The name of the bucket and the full path of the config file are set at beginning as follows:
```python
bucketConfig      =   "s3-testing-bucket-testing-ew1"
bucketKeyConfig   =   "pythonConfig/defaultConfig.json"
```

If there is a problem accessing the configuration file (e.g Permission denied),
there is a backup configuration in the form of a python dictionary object "defaultConfigBackUp",
which will be used instead.

The Python forwarder script is triggered when an email is received by SES and then stored in S3.
The script then processes the email and forwards it appropriately.

## Set up

1. Modify the values in either your external configuration file or in the backup configuration dictionary to
    specify the bucket used by SES to store the emails and the object prefix.
2. Modify the two forwarding mappings as follows:
```python
     'Forward_bySender_Mapping' : {
        'aws-example-email-replies@example.com' :[
            'example@email.com'
            ],
    },
    'Forward_byRecipient_Mapping' : {
        'noreply@aws.example.com' : [
            'anotherExample@email.com'
        ],
        '@exampleDomain.com' : [
            'example1.email@example.com',
            'example2.email@example.com'
        ],
    },
```
For more information on how to set up the whole Lambda in AWS read [here](https://github.com/arithmetric/aws-lambda-ses-forwarder)

## LICENSE

This project is released under the MIT License. Please check the LICENSE file for more details.


