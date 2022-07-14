from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pprint import pprint


import json
from jinja2 import Template
import yaml

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

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

with open('destination-rule.yaml', 'r') as file_reader:
    file_content = file_reader.read()

deployment_template = yaml.safe_load(file_content)
# deployment_template = Template(file_content)

# deployment_template = yaml.safe_load(deployment_template.render({
#     'test': 'from_jinja'
# }))

myclient = client.CustomObjectsApi()
#with client.CustomObjectsApi() as api_client:
    # Create an instance of the API class
    #api_instance = client.CustomObjectsApi(api_client)
group = 'networking.istio.io' # str | The custom resource's group name
version = 'v1alpha3' # str | The custom resource's version
plural = 'destinationrules' # str | The custom resource's plural name. For TPRs this would be lowercase plural kind.
body = deployment_template #json.dumps(body) # object | The JSON schema of the Resource to create.

try:
    #api_response = myclient.list_cluster_custom_object(group, version, plural)
    api_response = myclient.create_namespaced_custom_object(
        group=group, namespace="default", version=version, plural=plural, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CustomObjectsApi->create_cluster_custom_object: %s\n" % e)


with open('virtual-service-test.yaml', 'r') as file_reader:
    file_content = file_reader.read()

deployment_template = yaml.safe_load(file_content)
# deployment_template = Template(file_content)

# deployment_template = yaml.safe_load(deployment_template.render({
#     'test': 'from_jinja'
# }))

myclient = client.CustomObjectsApi()
#with client.CustomObjectsApi() as api_client:
    # Create an instance of the API class
    #api_instance = client.CustomObjectsApi(api_client)
group = 'networking.istio.io' # str | The custom resource's group name
version = 'v1alpha3' # str | The custom resource's version
plural = 'virtualservices' # str | The custom resource's plural name. For TPRs this would be lowercase plural kind.
body = deployment_template #json.dumps(body) # object | The JSON schema of the Resource to create.


try:
    #api_response = myclient.list_cluster_custom_object(group, version, plural)
    api_response = myclient.create_namespaced_custom_object(
        group=group, namespace="default", version=version, plural=plural, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CustomObjectsApi->create_cluster_custom_object: %s\n" % e)



