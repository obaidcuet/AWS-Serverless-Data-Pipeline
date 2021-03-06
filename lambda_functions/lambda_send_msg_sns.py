## libraries to load configuration from S3
from io import StringIO
import configparser

## to read env variables
import os

## boto3, python SDK for AWS Services
import boto3

## load configuration file from S3
s3 = boto3.client('s3')
config_file_data = s3.get_object(Bucket=os.environ['Config_File_S3_Bucket'], Key=os.environ['Config_File_S3_Key'])['Body'].read().decode('utf-8')

## parse confifuration file
config = configparser.ConfigParser()
config.sections()
config.readfp(StringIO(config_file_data))

## get all the configuration variables
#[basic]
emr_region = config['basic']['emr_region']

## initiate client
client_sns = boto3.client(
    'sns',
    region_name= emr_region,  
)


## invoke lambda function
def lambda_handler(event, context):
    client_sns.publish(
        TopicArn= os.environ['TopicArn'],
        Subject = os.environ['Subject'],
        Message= event["Message"]
    )
    
    return None