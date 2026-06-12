
from kubernetes.client import ApiException, AppsV1Api
from sw_operator.builders.deployment import build_deployment
import kopf
from sw_operator.utils.k8s import load_config

# function to handle the reconciliation of deployment
def reconcile_deployment(name, spec, namespace, owner, logger ):
    """
    Always build the desired Deployment from spec and applys it.
    Kubernetes server-side apply will create or update the resources automatically.

    :param name:
    :param spec:
    :param namespace:
    :param owner:
    :param logger:
    :return:
    """
    # Create the staticwebsite deployment
    desired=build_deployment(
        name=name,
        spec=spec,
        namespace=namespace,
        owner=owner
    )

    load_config()
    api = AppsV1Api()
    try:
        # Create the desired deployment
        api.create_namespaced_deployment(
            namespace=namespace,
            body=desired
        )
        logger.info(f'Deployment: {name} created')
    except ApiException as e:
        # if the resource already exists in cluster patch it
        # Using the strategic merge patch: k8s compute the diff server-side
        if e.status == 409:
            api.patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=desired
            )
            logger.info(f'Deployment: {name} reconciled')
        else:
            raise kopf.TemporaryError(f"Failed to reconcile the deployment: {e}", delay=10)
