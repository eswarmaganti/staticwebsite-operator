from sw_operator.clients.kubernetes import client
from kubernetes.client import V1Service, V1OwnerReference

# utility function to build the service manifest
def build_service(name: str, spec: dict, namespace: str, owner: V1OwnerReference ) -> V1Service:
    return client.V1Service(
        metadata=client.V1ObjectMeta(
            name=name,
            namespace=namespace,
            owner_references=[owner],
            labels={
                'app.kubernetes.io/name' : name,
                'app.kubernetes.io/managed-by': 'staticwebsite-operator',
                'app.kubernetes.io/component': 'staticwebsite'
            }
        ),
        spec=client.V1ServiceSpec(
            selector= {
                'app.kubernetes.io/name': name,
                'app.kubernetes.io/managed-by': 'staticwebsite-operator',
            },
            type='NodePort',
            ports=[
                client.V1ServicePort(
                    port=spec.get('port'),
                    target_port=spec.get('targetPort'),
                )
            ]
        )
    )