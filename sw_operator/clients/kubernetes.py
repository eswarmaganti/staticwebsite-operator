from kubernetes import client, config

# Load the kubeconfig
def _load_config():
    try:
        # running inside a cluster (production)
        config.load_incluster_config()
    except:
        # Running locally or in CT
        config.load_kube_config()

_load_config()

apps_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()
custom_api = client.CustomObjectsApi()