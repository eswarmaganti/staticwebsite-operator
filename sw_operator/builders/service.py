from sw_operator.clients.kubernetes import client

# utility function to build the service manifest
def build_service(name, spec, namespace, owner):
    return client.V1Service(
        metadata = client.V1ObjectMeta(
            name = name,
            namespace = namespace,
            owner_references = [owner],
        ),
        spec = client.V1ServiceSpec(
            selector =  {"app": name},
            type = "NodePort",
            ports = [
                client.V1ServicePort(
                    port = spec.get('port'),
                    target_port = spec.get('targetPort'),
                )
            ]
        )
    )