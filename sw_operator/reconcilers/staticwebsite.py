from sw_operator.reconcilers.deployment import reconcile_deployment
from sw_operator.reconcilers.service import reconcile_service
from sw_operator.reconcilers.status import reconcile_status
from sw_operator.builders.owner_reference import build_owner_reference

# function to reconcile the static website CR
def reconcile_staticwebsite(spec, name, namespace, body, patch, logger):
    owner_ref = build_owner_reference(body)

    reconcile_deployment(
        name=name,
        namespace=namespace,
        spec=spec,
        owner=owner_ref,
        logger=logger
    )
    reconcile_service(
        name=name,
        namespace=namespace,
        spec=spec,
        owner=owner_ref,
        logger=logger
    )

    reconcile_status(
        patch=patch,
        name=name,
        namespace=namespace,
        logger=logger
    )
