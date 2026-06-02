from sw_operator.clients.kubernetes import apps_v1
from kubernetes.client import ApiException

# function to reconcile the status of static website CR
def reconcile_status(patch, name, namespace, logger):

    # fetch the current deployment
    deployment = None
    try:
        deployment = apps_v1.read_namespaced_deployment(
            name = name,
            namespace = namespace
        )
    except ApiException as e:
        logger.error(e)

    patch.status['deploymentName'] = name
    patch.status['serviceName'] = name

    if deployment:
        patch.status['replicas'] = (
            deployment.status.replicas or 0
        )

        patch.status['readyReplicas'] = (
            deployment.status.ready_replicas or 0
        )

        patch.status['availableReplicas'] = (
            deployment.status.available_replicas or 0
        )

        # handle the phase
        desired = deployment.status.replicas
        ready = (
                deployment.status.ready_replicas or 0
        )

        patch.status['phase'] = (
            "Running" if desired == ready
            else "Progressing" if ready > 0
            else "Pending"
        )