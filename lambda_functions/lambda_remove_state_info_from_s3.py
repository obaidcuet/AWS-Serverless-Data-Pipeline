## libraries to load configuration from S3
from io import StringIO
import configparser

## boto3, python SDK for AWS Services
import boto3

## to read env variables
import os

## load configuration file from S3
s3 = boto3.client('s3')
config_file_data = s3.get_object(Bucket=os.environ['Config_File_S3_Bucket'], Key=os.environ['Config_File_S3_Key'])['Body'].read().decode('utf-8')

## parse confifuration file
config = configparser.ConfigParser()
config.sections()
config.readfp(StringIO(config_file_data))

## get required configuration variables
emr_region = config['basic']['emr_region']


## S3 location to store state info
state_info_file_s3_bucket = os.environ['State_Info_File_S3_Bucket']
state_info_file_s3_key = os.environ['State_Info_File_S3_Key']


## S3 client
client_s3 = boto3.client(
    's3',
    region_name= emr_region
)


## invoke lambda function
def lambda_handler(event, context):

    # write empty file to S3
    response_write_s3 = client_s3.put_object(Body='', Bucket=state_info_file_s3_bucket, Key=state_info_file_s3_key)
        
    return response_write_s3