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
GATEWAY_NAME = os.environ.get("GATEWAY_NAME", "control-plane-gateway")
GATEWAY_NAMESPACE = os.environ.get("GATEWAY_NAMESPACE", "default")
NAMESPACE = os.environ.get("K8S_NAMESPACE", "flighty-ai")

# TODO: impersonate the user account so we can discover permissions issues sooner
# core_client = client.CoreV1Api(header_name='Impersonate-User', header_value='flighty-control-plane')

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

def create_destination_rule(endpoint_name, namespace=NAMESPACE):
    '''creates a destination rule from the YAML file in this directory'''
    file_path = os.path.join(__location__, 'destination-rule.yaml')

    logger.debug('we are in create_destination_rule')

    myclient = client.CustomObjectsApi()
    plural = 'destinationrules'
    body = load_and_parse_yaml(
        file_path,
        endpoint_name=endpoint_name,
        gateway_name=GATEWAY_NAME,
        gateway_namespace=GATEWAY_NAMESPACE)

    try:
        api_response = myclient.create_namespaced_custom_object(
            group=GROUP, namespace=namespace, version=VERSION, plural=plural, body=body)
        logger.debug(api_response)
    except ApiException as e:
        logger.debug(
            "Exception when calling CustomObjectsApi->create_cluster_custom_object: %s\n", e)
        raise e

def create_deployment(handler_name, handler_version, model_artifact, 
    model_version, code_artifact, code_version, endpoint_name):
    '''Creates a deployment using the deployment-handler.yaml template'''

    file_path = os.path.join(__location__, 'deployment-handler.yaml')
    deployment_name = f'{endpoint_name}-{handler_name}-{handler_version}'
    body = load_and_parse_yaml(
        file_path, deployment_name=deployment_name, model_artifact=model_artifact,
        model_version=model_version, code_version=code_version,
        code_artifact=code_artifact, endpoint_name=endpoint_name, handler_name=handler_name,
        namespace=NAMESPACE)
    api = client.AppsV1Api()

    try:
        api_response = api.create_namespaced_deployment(
            body=body, namespace=NAMESPACE
        )
        logger.debug(api_response)
    except ApiException as e:
        logger.debug("Exception when calling create_namespaced_deployment: %s\n", e)
        raise e

def create_service(handler_name, handler_version, endpoint_name):
    '''Creates a service using the service-handler.yaml template'''

    file_path = os.path.join(__location__, 'service-handler.yaml')
    service_name = f'{endpoint_name}-{handler_name}-{handler_version}'
    body = load_and_parse_yaml(
        file_path, service_name=service_name, handler_name=handler_name, namespace=NAMESPACE)
    api = client.CoreV1Api()

    try:
        api_response = api.create_namespaced_service(
            body=body, namespace=NAMESPACE
        )
        logger.debug(api_response)
    except ApiException as e:
        logger.debug("Exception when calling create_namespaced_service: %s\n", e)
        raise e


def add_handler_to_endpoint(endpoint_name, handler_name):
    '''Modify virtual service definition to insert the handler with 100% of traffic'''

    myclient = client.CustomObjectsApi()
    plural = 'virtualservices'
    response=myclient.get_namespaced_custom_object(
        group=GROUP, 
        version=VERSION, 
        namespace=NAMESPACE, 
        plural=plural, 
        name=endpoint_name)

    # TODO - this is EXTREMELY brittle, need to add logic to deal with lists of routes
    # This code only works for the very first handler behind the endpoint, also doesn't support
    # invoking the model directly via /endpoint_name/handler syntax
    response['spec']['http'][0]['route'][0]['destination']['host'] = f'{handler_name}-service'
    # Reapply
    try:
        api_response = myclient.patch_namespaced_custom_object(name=endpoint_name,
            group=GROUP, namespace=NAMESPACE, version=VERSION, plural=plural, body=response)
        logger.debug(api_response)
    except ApiException as e:
        logger.debug("Exception when calling create_namespaced_custom_object: %s\n", e)
        raise e


def get_endpoint_body(endpoint_name):
    file_path = os.path.join(__location__, 'virtual-service.yaml')

    body = load_and_parse_yaml(
        file_path, 
        endpoint_name=endpoint_name,
        gateway_name=GATEWAY_NAME,
        gateway_namespace=GATEWAY_NAMESPACE)
    return body


def create_virtual_service(endpoint_name):
    '''Creates a virtual service with the specified name in the specified namespace'''

    myclient = client.CustomObjectsApi()
    plural = 'virtualservices'
    body = get_endpoint_body(endpoint_name=endpoint_name)
    try:
        api_response = myclient.create_namespaced_custom_object(
            group=GROUP, namespace=NAMESPACE, version=VERSION, plural=plural, body=body)
        logger.debug(api_response)
    except ApiException as e:
        logger.debug("Exception when calling create_namespaced_custom_object: %s\n", e)
        raise e

def delete_virtual_service(endpoint_name):
    '''Deletes virtual service with specified name'''
    myclient = client.CustomObjectsApi()
    plural = 'virtualservices'
    try:
        api_response = myclient.delete_namespaced_custom_object(name=endpoint_name,
            group=GROUP, namespace=NAMESPACE, version=VERSION, plural=plural)
        logger.debug(api_response)
    except ApiException as e:
        logger.debug("Exception when calling delete_namespaced_custom_object: %s\n", e)
        raise e

def delete_deployment(handler_name, handler_version, endpoint_name):
    '''Deletes virtual service with specified name'''
    deployment_name = f'{endpoint_name}-{handler_name}-{handler_version}'
    api = client.AppsV1Api()
    try:
        api_response =api.delete_namespaced_deployment(name=deployment_name,
            namespace=NAMESPACE)
        logger.debug(api_response)
    except ApiException as e:
        logger.debug("Exception when calling delete_namespaced_custom_object: %s\n", e)
        raise e

def delete_service(handler_name, handler_version, endpoint_name):
    '''Creates a service using the service-handler.yaml template'''
    service_name = f'{endpoint_name}-{handler_name}-{handler_version}'
    api = client.CoreV1Api()

    try:
        api_response = api.delete_namespaced_service(
            name=service_name, namespace=NAMESPACE
        )
        logger.debug(api_response)
    except ApiException as e:
        logger.debug("Exception when calling delete_namespaced_service: %s\n", e)
        raise e