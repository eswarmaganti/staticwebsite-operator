from sw_operator.clients.kubernetes import client
from kubernetes.client import V1Deployment, V1OwnerReference


# utility function to create the deployment specification
def build_deployment(name: str, spec: dict, namespace: str, owner: V1OwnerReference) -> V1Deployment:
    return client.V1Deployment(
        metadata = client.V1ObjectMeta(
            name = name,
            namespace = namespace,
            owner_references=[owner],

        ),
        spec = client.V1DeploymentSpec(
            replicas = spec.get('replicas', 1),
            selector = client.V1LabelSelector(
                match_labels={
                    "app.kubernetes.io/name": name,
                    "app.kubernetes.io/managed-by": "staticwebsite-operator",
                }
            ),
            template = client.V1PodTemplateSpec(
                metadata = client.V1ObjectMeta(
                    name=name,
                    labels={
                        "app.kubernetes.io/name": name,
                        "app.kubernetes.io/managed-by": "staticwebsite-operator",
                        "app.kubernetes.io/component" : "staticwebsite"
                    },
                ),
                spec = client.V1PodSpec(
                    containers = [
                        client.V1Container(
                            name = name,
                            image = spec.get('image'),
                            ports = [
                                client.V1ContainerPort(
                                    container_port = spec.get('targetPort'),
                                )
                            ]
                        )
                    ]
                )
            )
        )
    )