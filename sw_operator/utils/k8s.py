# util method to load the config file
from kubernetes import config
from kubernetes.config.config_exception import ConfigException

def load_config():
    try:
        config.load_incluster_config()
    except ConfigException:
        config.load_kube_config()


