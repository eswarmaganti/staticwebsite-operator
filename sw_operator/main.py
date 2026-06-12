import logging
import kopf
import sw_operator.handlers.main


@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **kwargs):
    settings.posting.level = logging.WARNING
    settings.persistence.finalizer = 'platform.eswar.dev/kopf-finalizer'



# decorator to make the controller access the cluster using the service account when deployed as a container
# else use the kubeconfig file available to access the cluster
@kopf.on.login()
def login_fn(**kwargs):
    credentials = kopf.login_with_service_account(**kwargs)
    if credentials is not None:
        return credentials
    return kopf.login_with_kubeconfig(**kwargs)


if __name__ == '__main__':
    kopf.run()