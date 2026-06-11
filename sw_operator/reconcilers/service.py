from kubernetes.client import ApiException, CoreV1Api
from sw_operator.builders.service import build_service
import kopf

# function to reconcile the service
def reconcile_service(name, namespace, spec, owner, logger) -> None:
    """
    Always build the desired Service from the spec and apply it.
    The Kubernetes server-side apply will create-or-update the resources accordingly.

    :param name:
    :param namespace:
    :param spec:
    :param owner:
    :param logger:
    :return: None
    """
    desired=build_service(
        name=name,
        namespace=namespace,
        spec=spec,
        owner=owner
    )
    api = CoreV1Api()
    try:
        api.create_namespaced_service(
            namespace=namespace,
            body=desired
        )
        logger.info(f'Service: {name} created')
    except ApiException as e:
        if e.status == 409:
            api.patch_namespaced_service(
                name=name,
                namespace=namespace,
                body=desired
            )
            logger.info(f'Service: {name} reconciled')
        else:
            raise kopf.TemporaryError(f"Failed to  reconcile the service: {e}", delay=10)
