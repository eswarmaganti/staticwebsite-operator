from kubernetes.client import V1OwnerReference, ApiException
from sw_operator.clients.kubernetes import client
from sw_operator.builders.gateway import build_httproute, build_gateway


def reconcile_gateway(name: str, namespace: str, spec: dict, owner: V1OwnerReference, logger) -> None:
    custom_objects_api=client.CustomObjectsApi()

    gateway = build_gateway(
        name=name,
        namespace=namespace,
        spec=spec,
        owner=owner,
    )
    http_route = build_httproute(
        name=name,
        namespace=namespace,
        spec=spec,
        owner=owner,
    )

    # create the GW if it's not exist
    try:
        current_gateway = custom_objects_api.get_namespaced_custom_object(
            name=name,
            namespace=namespace,
            group='gateway.networking.k8s.io',
            version='v1',
            plural='gateways',
        )
        logger.info(f"Reconciling Gateway: {name}")
        custom_objects_api.patch_namespaced_custom_object(
            name=name,
            namespace=namespace,
            group='gateway.networking.k8s.io',
            version='v1',
            plural='gateways',
            body=gateway,
        )
        logger.info(f"Successfully Reconcilled Gateway: {name}")
        #TODO: update reconciliation logic here

    except ApiException as e:
        logger.info(f"Creating Gateway: {name}")
        custom_objects_api.create_namespaced_custom_object(
            namespace=namespace,
            group='gateway.networking.k8s.io',
            version="v1",
            plural='gateways',
            body=gateway
        )
        logger.info(f"Successfully created the Gateway: {name}")

    # create the GW if it's not exist
    try:
        current_httproute = custom_objects_api.get_namespaced_custom_object(
            name=name,
            namespace=namespace,
            group='gateway.networking.k8s.io',
            version='v1',
            plural='httproutes',
        )
        #TODO: update reconciliation logic here
        logger.info(f"Reconciling HTTPRoute: {name}")
        custom_objects_api.patch_namespaced_custom_object(
            name=name,
            namespace=namespace,
            group='gateway.networking.k8s.io',
            version='v1',
            body=http_route,
            plural='httproutes',
        )
        logger.info(f"Successfully Reconciled HTTPRoute: {name}")
    except ApiException as e:
        logger.info(f"Creating HTTPRoute: {name}")
        custom_objects_api.create_namespaced_custom_object(
            namespace=namespace,
            group='gateway.networking.k8s.io',
            version="v1",
            plural='httproutes',
            body=http_route
        )
        logger.info(f"Successfully created the HTTPRoute: {name}")