from sw_operator.clients.kubernetes import apps_v1
from kubernetes.client import ApiException
from sw_operator.builders.deployment import build_deployment
from sw_operator.utils import deployment_needs_reconciliation


# function to handle the reconciliation of deployment
def reconcile_deployment(name, spec, namespace, owner, logger, ):
    # Create the staticwebsite deployment
    desired_deployment = build_deployment(
        name = name,
        spec = spec,
        namespace = namespace,
        owner = owner
    )

    try:
        # read the current deployment
        current_deployment = apps_v1.read_namespaced_deployment(
            name=name,
            namespace=namespace
        )

        # handling the patch logic for deployment
        if deployment_needs_reconciliation(
                desired = desired_deployment, current = current_deployment):
            logger.info(f"Deployment: {name} needs reconciliation")
            apps_v1.patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=desired_deployment
            )
        logger.info(f"Deployment: {name} reconciled")

    except ApiException as e:

        # handling the deployment creation
        logger.info(f"Creating the deployment: {name}")

        apps_v1.create_namespaced_deployment(
            namespace=namespace,
            body=desired_deployment
        )
    logger.info(f"Created the deployment: {name}")