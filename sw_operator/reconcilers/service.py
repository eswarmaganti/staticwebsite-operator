from kubernetes.client import ApiException
from sw_operator.clients.kubernetes import core_v1
from sw_operator.builders.service import build_service
from sw_operator.utils import service_needs_reconciliation

# function to reconcile the service
def reconcile_service(name, namespace, spec, owner, logger):
    desired_service = build_service(
        name=name,
        namespace=namespace,
        spec = spec,
        owner = owner
    )

    try:
        # fetch the current running service
        curr_service = core_v1.read_namespaced_service(
            name=name,
            namespace=namespace
        )
        logger.info(f"Reconciling the service {name}")
        if service_needs_reconciliation(
            current = curr_service,
            desired = desired_service
        ):
            core_v1.patch_namespaced_service(
                name=name,
                namespace=namespace,
                body=desired_service
            )
        logger.info(f"Reconciled the service {name}")
    except ApiException as e:
        # Create the service
        logger.info(f"Creating the service {name}")
        core_v1.create_namespaced_service(
            namespace = namespace,
            body = desired_service
        )
        logger.info(f"Created the service {name}")
