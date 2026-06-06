from kubernetes.client import V1OwnerReference, ApiException
from sw_operator.clients.kubernetes import client
from sw_operator.builders.gateway import build_httproute, build_gateway
import kopf

def reconcile_gateway(name: str, namespace: str, spec: dict, owner: V1OwnerReference, logger) -> None:

    # static constants
    GROUP = "gateway.networking.k8s.io"
    VERSION = "v1"

    custom_objects_api=client.CustomObjectsApi()

    desired_gw = build_gateway(
        name=name,
        namespace=namespace,
        spec=spec,
        owner=owner,
    )
    desired_route = build_httproute(
        name=name,
        namespace=namespace,
        spec=spec,
        owner=owner,
    )

    # reconciliation logic for Gateway resource
    try:
        custom_objects_api.create_namespaced_custom_object(
            namespace=namespace,
            group=GROUP,
            version=VERSION,
            plural='gateways',
            body=desired_gw,
        )
        logger.info(f"Gateway: {name} created")

    except ApiException as e:
        if e.status == 409:
            custom_objects_api.patch_namespaced_custom_object(
                name=name,
                namespace=namespace,
                group=GROUP,
                version=VERSION,
                plural='gateways',
                body=desired_gw,
            )
            logger.info(f"Gateway: {name} reconciled")
        else:
            raise kopf.TemporaryError(f"Failed to reconcile gateway: {e}", delay=10)

    # reconciliation logic for HTTPRoute resource
    try:
        custom_objects_api.create_namespaced_custom_object(
            namespace=namespace,
            group=GROUP,
            version=VERSION,
            plural='httproutes',
            body=desired_route,
        )
        logger.info(f"HTTPRoute: {name} created")
    except ApiException as e:
        if e.status == 409:
            custom_objects_api.patch_namespaced_custom_object(
                name=name,
                namespace=namespace,
                group=GROUP,
                version=VERSION,
                plural='httproutes',
                body=desired_route,
            )
            logger.info(f"HTTPRoute: {name} reconciled")
        else:
            raise kopf.TemporaryError(f"Failed to reconcile HTTPRoute: {e}", delay=10)