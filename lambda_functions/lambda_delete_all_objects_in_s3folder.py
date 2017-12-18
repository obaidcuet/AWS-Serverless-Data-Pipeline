## delete all file in target s3 folder

## boto3, python SDK for AWS Services
import boto3

## to read env variables
import os

## load configuration file from S3
client_s3 = boto3.client('s3')
#config_file_data = s3.get_object(Bucket=os.environ['Config_File_S3_Bucket'], Key=os.environ['Config_File_S3_Key'])['Body'].read().decode('utf-8')

## Create a Paginator as boto3 limit 1000 objects
paginator = client_s3.get_paginator('list_objects_v2')
# set the filters
operation_parameters = {'Bucket': os.environ['Target_Folder_S3_Bucket'],
						'Prefix': os.environ['Target_Folder_S3_Key'],
						'PaginationConfig': {'PageSize': 100}}
# paginate the result
page_iterator = paginator.paginate(**operation_parameters)						

def lambda_handler(event, context):
    # loop for contents in each page
    for page in page_iterator:
        # loop for objects in each page
        if 'Contents' in page:
    	    for dict_item in page['Contents']:
    		    curr_object = dict_item.get('Key') # get current object
    		    response_delete = client_s3.delete_object( Bucket=os.environ['Target_Folder_S3_Bucket'], Key=curr_object )
    		    # check delete successful
    		    if response_delete['ResponseMetadata']['HTTPStatusCode'] not in [200, 204] :
    		        print ('ERROR: Failed to delete object:'+curr_object)
    		        return 'ERROR'
                
    # if no error so far then all SUCCESS
    return 'SUCCESS'