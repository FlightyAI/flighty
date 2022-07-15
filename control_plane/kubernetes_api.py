"""
kubernetes_api

Helper functions to interact with the kubernetes API from within the cluster
"""

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


def load_and_parse_yaml(file_path, **kwargs):
    '''Loads a YAML file from local directory and fills in placeholders'''
    with open(file_path, 'r', encoding='utf-8') as file_reader:
        file_content = file_reader.read()
    # deployment_template = yaml.safe_load(file_content)
    deployment_template = Template(file_content)

    deployment_template = yaml.safe_load(deployment_template.render(**kwargs))
    logger.debug('deployment template is %s', deployment_template)
    return deployment_template

def create_destination_rule(endpoint_name, namespace='default'):
    '''creates a destination rule from the YAML file in this directory'''
    file_path = os.path.join(__location__, 'destination-rule.yaml')

    logger.debug('we are in create_destination_rule')

    myclient = client.CustomObjectsApi()
    plural = 'destinationrules'
    body = load_and_parse_yaml(file_path, endpoint_name=endpoint_name)

    try:
        api_response = myclient.create_namespaced_custom_object(
            group=GROUP, namespace=namespace, version=VERSION, plural=plural, body=body)
        logger.debug(api_response)
    except ApiException as e:
        logger.debug(
            "Exception when calling CustomObjectsApi->create_cluster_custom_object: %s\n", e)
        raise e

def create_deployment(handler_name, model_artifact, 
    model_version, code_artifact, code_version, namespace='default'):
    '''Creates a deployment using the deployment-handler.yaml template'''

    file_path = os.path.join(__location__, 'deployment-handler.yaml')
    body = load_and_parse_yaml(
        file_path, handler_name=handler_name, model_artifact=model_artifact,
        model_version=model_version, code_version=code_version,
        code_artifact=code_artifact)
    api = client.AppsV1Api()

    try:
        api_response = api.create_namespaced_deployment(
            body=body, namespace=namespace
        )
        logger.debug(api_response)
    except ApiException as e:
        logger.debug("Exception when calling create_namespaced_deployment: %s\n", e)
        raise e

def create_service(handler_name, namespace='default'):
    '''Creates a service using the service-handler.yaml template'''

    file_path = os.path.join(__location__, 'service-handler.yaml')
    body = load_and_parse_yaml(
        file_path, handler_name=handler_name)
    api = client.CoreV1Api()

    try:
        api_response = api.create_namespaced_service(
            body=body, namespace=namespace
        )
        logger.debug(api_response)
    except ApiException as e:
        logger.debug("Exception when calling create_namespaced_service: %s\n", e)
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

    myclient = client.CustomObjectsApi()
    plural = 'virtualservices'
    body = load_and_parse_yaml(file_path, endpoint_name=endpoint_name)

    try:
        api_response = myclient.create_namespaced_custom_object(
            group=GROUP, namespace=namespace, version=VERSION, plural=plural, body=body)
        logger.debug(api_response)
    except ApiException as e:
        logger.debug("Exception when calling create_namespaced_custom_object: %s\n", e)
        raise e
