from kubernetes import client, config

# Load the kubeconfig
config.load_kube_config()

apps_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()