from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()

containers = [client.V1Container(name='test', image='docker.io/gvashishtha/flighty:test')]
spec = client.V1PodSpec(
    containers=containers, 
    image_pull_secrets=[client.V1LocalObjectReference(name='regcred')])
pod = client.V1Pod(metadata=client.V1ObjectMeta(name='test1'), spec=spec)


print("Listing pods with their IPs:")
v1.create_namespaced_pod(namespace='default', body=pod)
