## start cluster using boto3
# initially it will have 1 master and some core instances as on demand
# other core instances will try to be spot for 10 minutes, afer that will be ondemand
# only EMR no steps/jobs
    
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
emr_name = config['basic']['emr_name']
log_on_s3 = config['basic']['log_on_s3']
emr_version = config['basic']['emr_version']

#[instances]
master_instance_type = config['instances']['master_instance_type']
worker_instance_type = config['instances']['worker_instance_type']
ondemand_worker_count = int(config['instances']['ondemand_worker_count'])

#[access]
subnet_id = config['access']['subnet_id']
ec2_keypair_name = config['access']['ec2_keypair_name']

#[metastore]
metastore_factory_class = config['metastore']['metastore_factory_class']

#[spot]
spot_worker_count = int(config['spot']['spot_worker_count'])
spot_worker_increment_count = int(config['spot']['spot_worker_increment_count'])
spot_price_pct_of_ondemand = float(config['spot']['spot_price_pct_of_ondemand'])
spot_timeout_duration_minutes = int(config['spot']['spot_timeout_duration_minutes'])
spot_timeout_action = config['spot']['spot_timeout_action']
spot_block_duration_minutes = int(config['spot']['spot_block_duration_minutes'])

## initiate client
client_emr = boto3.client(
    'emr',
    region_name= emr_region,  
)

## invoke lambda function
def lambda_handler(event, context):
    
    # start the EMR cluster   
    emrcluster_start = client_emr.run_job_flow(
        Name= emr_name,
        LogUri= log_on_s3,
        ReleaseLabel= emr_version,
        Instances={
            'InstanceFleets': [
                {
                    'Name': 'EMR Master',
                    'InstanceFleetType': 'MASTER',
                    'TargetOnDemandCapacity': 1,
                    'InstanceTypeConfigs': [
                        {
                            'InstanceType': master_instance_type,
                        },
                    ]
                },
                {
                    'Name': 'EMR Workers',
                    'InstanceFleetType': 'CORE',
                    'TargetOnDemandCapacity': ondemand_worker_count,
                    'TargetSpotCapacity': spot_worker_count,
                    'InstanceTypeConfigs': [
                        {
                            'InstanceType': worker_instance_type,
                            'BidPriceAsPercentageOfOnDemandPrice': spot_price_pct_of_ondemand,
                        },
                    ],
                    'LaunchSpecifications': {
                        'SpotSpecification': {
                            'TimeoutDurationMinutes': spot_timeout_duration_minutes,
                            'TimeoutAction': spot_timeout_action,
                            'BlockDurationMinutes': spot_block_duration_minutes,
                        }
                    }
                }
            ],
            'KeepJobFlowAliveWhenNoSteps': True,
            'TerminationProtected': False,
            'Ec2SubnetId': subnet_id,
            'Ec2KeyName': ec2_keypair_name,
        },
        Applications=[
            {'Name': 'Spark'},
            {'Name': 'Hive'},
        ],
        Configurations=[
            {
                'Classification':'hive-site',
                'Properties':{'hive.metastore.client.factory.class': metastore_factory_class }
            },
            {
                'Classification':'spark-hive-site',
                'Properties':{'hive.metastore.client.factory.class': metastore_factory_class }
            }
         ],
        VisibleToAllUsers=True,
        JobFlowRole='EMR_EC2_DefaultRole',
        ServiceRole='EMR_DefaultRole',
        Tags=[
            {
                'Key': 'Name',
                'Value': 'EMR with Boto',
            },
            {
                'Key': 'TerminationVal',
                'Value': 'OK', 
            },
        ],
    )
    # return EMR Start response to pass to next steps
    return {"ClusterId" : emrcluster_start['JobFlowId'], "Status" : "STARTING" }

