from kubernetes import client, config
from kubernetes.config import ConfigException

apps_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()
custom_api = client.CustomObjectsApi()