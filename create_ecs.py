#!/usr/bin/env python3

import boto3
import random
import string

client = boto3.client('ecs')

def create_service():

  response = client.create_service(
    cluster='DevCluster',
    serviceName='flighty_public1',
    taskDefinition='Flighty',
    # loadBalancers=[
    #     {
    #         'targetGroupArn': 'string',
    #         'loadBalancerName': 'string',
    #         'containerName': 'string',
    #         'containerPort': 123
    #     },
    # ],
    # serviceRegistries=[
    #     {
    #         'registryArn': 'string',
    #         'port': 123,
    #         'containerName': 'string',
    #         'containerPort': 123
    #     },
    # ],
    desiredCount=0,
    clientToken=''.join(random.choices(string.ascii_uppercase + string.digits, k=32)),
    launchType='FARGATE',
    # capacityProviderStrategy=[
    #     {
    #         'capacityProvider': 'string',
    #         'weight': 123,
    #         'base': 123
    #     },
    # ],
    #platformVersion='string',
    #role='string',
    # deploymentConfiguration={
    #     'deploymentCircuitBreaker': {
    #         'enable': True|False,
    #         'rollback': True|False
    #     },
    #     'maximumPercent': 123,
    #     'minimumHealthyPercent': 123
    # },
    networkConfiguration={
        'awsvpcConfiguration': {
            'subnets': [
                'subnet-07243a455b6324931',
            ],
            'securityGroups': [
                'sg-019453ec44d351a52',
            ],
            'assignPublicIp': 'ENABLED'
        }
    },
    #healthCheckGracePeriodSeconds=123,
    #schedulingStrategy='REPLICA'|'DAEMON',
    # deploymentController={
    #     'type': 'ECS'|'CODE_DEPLOY'|'EXTERNAL'
    # },
    tags=[
        {
            'key': 'string',
            'value': 'string'
        },
    ],
    # enableECSManagedTags=True|False,
    # propagateTags='TASK_DEFINITION'|'SERVICE'|'NONE',
    # enableExecuteCommand=True|False
)
  print(response)

def increment_service():
  response = client.update_service(
    cluster='DevCluster',
    service='flighty_public1',
    desiredCount=1,
    #clientToken=''.join(random.choices(string.ascii_uppercase + string.digits, k=32)),
)


if (__name__=='__main__'):
  increment_service()
  # create_service()