from kubernetes.client import V1OwnerReference, ApiException, CustomObjectsApi
from sw_operator.builders.gateway import build_httproute, build_gateway
import kopf

# static constants
GROUP = "gateway.networking.k8s.io"
VERSION = "v1"

def reconcile_gateway(name: str, namespace: str, spec: dict, owner: V1OwnerReference, logger) -> None:

    reconcile_gateway_resource(name=name, namespace=namespace, spec=spec, owner=owner, logger=logger)
    reconcile_httproute_resource(name=name, namespace=namespace, spec=spec, owner=owner, logger=logger)

def reconcile_gateway_resource(name: str, namespace: str, spec: dict, owner: V1OwnerReference, logger):
    # reconciliation logic for Gateway resource
    desired_gw = build_gateway(
        name=name,
        namespace=namespace,
        spec=spec,
        owner=owner,
    )
    try:
        api = CustomObjectsApi()
        api.create_namespaced_custom_object(
            namespace=namespace,
            group=GROUP,
            version=VERSION,
            plural='gateways',
            body=desired_gw,
        )
        logger.info(f"Gateway: {name} created")

    except ApiException as e:
        if e.status == 409:
            api.patch_namespaced_custom_object(
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

def reconcile_httproute_resource(name: str, namespace: str, spec: dict, owner: V1OwnerReference, logger):
    # reconciliation logic for HTTPRoute resource
    desired_route = build_httproute(
        name=name,
        namespace=namespace,
        spec=spec,
        owner=owner,
    )
    api = CustomObjectsApi()
    try:
        api.create_namespaced_custom_object(
            namespace=namespace,
            group=GROUP,
            version=VERSION,
            plural='httproutes',
            body=desired_route,
        )
        logger.info(f"HTTPRoute: {name} created")
    except ApiException as e:
        if e.status == 409:
            api.patch_namespaced_custom_object(
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