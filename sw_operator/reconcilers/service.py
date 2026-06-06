from kubernetes.client import ApiException
from sw_operator.clients.kubernetes import core_v1
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

    try:
        core_v1.create_namespaced_service(
            body=desired,
            namespace=namespace
        )
        logger.info(f'Service: {name} created')
    except ApiException as e:
        if e.status == 409:
            core_v1.patch_namespaced_service(
                name=name,
                namespace=namespace,
                body=desired
            )
            logger.info(f'Service: {name} reconciled')
        else:
            raise kopf.TemporaryError(f"Failed to  reconcile the service: {e}", delay=10)
