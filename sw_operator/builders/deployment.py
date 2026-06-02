from sw_operator.clients.kubernetes import client

# utility function to create the deployment specification
def build_deployment(name, spec, namespace, owner):
    return client.V1Deployment(
        metadata = client.V1ObjectMeta(
            name = name,
            namespace = namespace,
            owner_references=[owner],
        ),
        spec = client.V1DeploymentSpec(
            replicas = spec.get('replicas', 1),
            selector = client.V1LabelSelector(
                match_labels={"app": name}
            ),
            template = client.V1PodTemplateSpec(
                metadata = client.V1ObjectMeta(
                    name=name,
                    labels={"app": name},
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