"""
kubernetes_api

Helper functions to interact with the kubernetes API from within the cluster
"""
from pprint import pprint

import logging
import os

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from jinja2 import Template
import yaml

logger = logging.getLogger('kubernetes_api')

GROUP = 'networking.istio.io' # str | The custom resource's group name
VERSION = 'v1alpha3'
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Try loading cluster config, fall back to local
try:
    config.load_incluster_config()
except config.config_exception.ConfigException:
    config.load_kube_config()

def create_destination_rule(endpoint_name, namespace='default'):
    '''creates a destination rule from the YAML file in this directory'''
    file_path = os.path.join(__location__, 'destination-rule.yaml')

    logger.debug('we are in create_destination_rule')
    with open(file_path, 'r', encoding='utf-8') as file_reader:
        file_content = file_reader.read()
    # deployment_template = yaml.safe_load(file_content)
    deployment_template = Template(file_content)

    deployment_template = yaml.safe_load(deployment_template.render({
        'endpoint_name': endpoint_name
    }))
    logger.debug('deployment template is %s', deployment_template)

    myclient = client.CustomObjectsApi()
    plural = 'destinationrules'
    body = deployment_template

    try:
        api_response = myclient.create_namespaced_custom_object(
            group=GROUP, namespace=namespace, version=VERSION, plural=plural, body=body)
        logger.debug(api_response)
    except ApiException as e:
        logger.debug(f"Exception when calling CustomObjectsApi->create_cluster_custom_object: {e}\n")
        raise e


#v1 = client.CoreV1Api()
#configuration = v1.api_client.configuration
#configuration.host = "'https://kubernetes.docker.internal:6443'"
# #v1 = client.CoreV1Api()

# # containers = [client.V1Container(name='test', image='docker.io/gvashishtha/flighty:test')]
# # spec = client.V1PodSpec(
# #     containers=containers,
# #     image_pull_secrets=[client.V1LocalObjectReference(name='regcred')])
# # pod = client.V1Pod(metadata=client.V1ObjectMeta(name='test1'), spec=spec)


# # print("Listing pods with their IPs:")
# # v1.create_namespaced_pod(namespace='default', body=pod)

def create_virtual_service(endpoint_name, namespace='default'):
    '''Creates a virtual service with the specified name in the specified namespace'''
    file_path = os.path.join(__location__, 'virtual-service.yaml')
    with open(file_path, 'r', encoding='utf-8') as file_reader:
        file_content = file_reader.read()

    #deployment_template = yaml.safe_load(file_content)
    deployment_template = Template(file_content)

    deployment_template = yaml.safe_load(deployment_template.render({
        'endpoint_name': endpoint_name
    }))

    myclient = client.CustomObjectsApi()
    plural = 'virtualservices'
    body = deployment_template

    try:
        api_response = myclient.create_namespaced_custom_object(
            group=GROUP, namespace=namespace, version=VERSION, plural=plural, body=body)
        logger.debug(api_response)
    except ApiException as e:
        logger.debug(f"Exception when calling CustomObjectsApi->create_cluster_custom_object: {e}\n")
        raise e
