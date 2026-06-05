from kubernetes.client import ApiException
from sw_operator.clients.kubernetes import client
from sw_operator.config import GROUP, VERSION, PLURAL
import kopf

def reconcile_status(name, namespace, body, logger) -> None:
    """
    Function to reconcile the status of the custom resource StaticWebsite by listening on deployment 'status.readyReplicas' field changes

    :param name:
    :param namespace:
    :param body:
    :param logger:
    :return: None
    """

    # fetch the owner_ref and sw_name from the body
    owner_refs = body.get('metadata', {}).get('ownerReferences', [])
    sw_name = next(ref['name'] for ref in owner_refs if ref.get('kind') == 'StaticWebsite' )

    if not sw_name:
        logger.debug(f'Deployment has no StaticWebsite owner, skipping the status reconciliation')
        return

    # fetch the required fields
    deployment_status = body.get('status', {})
    desired_replicas = body.get('spec', {}).get('replicas', 0)
    available_replicas = deployment_status.get('availableReplicas', 0)
    ready_replicas = deployment_status.get('readyReplicas', 0)
    conditions = deployment_status.get('conditions', [])

    # deriving the phase from deployment status conditions
    available_cond = next((c for c in conditions if c.get('type') == 'Available'), None)
    progressing_cond = next((c for c in conditions if c.get('type') == 'Progressing'), None)

    if available_cond and available_cond.get('status') == 'True':
        phase = 'Ready'
    elif progressing_cond and progressing_cond.get('status') == 'True':
        phase = 'Progressing'
    else:
        phase = 'Degraded'

    logger.info(f"Syncing status: phase={phase}, available/desired={available_replicas}/{desired_replicas}, ready={ready_replicas}")

    # Reconcile the CR status
    try:
        custom_objects_api = client.CustomObjectsApi()
        custom_objects_api.patch_namespaced_custom_object(
            group=GROUP,
            version=VERSION,
            plural=PLURAL,
            name=sw_name,
            namespace=namespace,
            body={
                'status': {
                    'phase': phase,
                    'readyReplicas': ready_replicas,
                    'availableReplicas': available_replicas,
                    'desiredReplicas': desired_replicas,
                    'deploymentName': name,
                }
            }
        )
        logger.info(f'CR: {sw_name} Status sync is successfully completed')
    except ApiException as e:
        if e.status == 404:
            # CR was deleted before the status is patched
            logger.warning(f'Staticwebsite/{sw_name} is not found, likely deleted, skipping the status reconciliation')
        else:
            raise kopf.TemporaryError(f'Failed to patch status: {e}', delay=10)

