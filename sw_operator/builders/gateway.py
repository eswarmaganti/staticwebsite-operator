from sw_operator.clients.kubernetes import client
from kubernetes.client import V1OwnerReference


def build_gateway(name: str, namespace: str, spec: dict, owner: V1OwnerReference) -> dict:
    return {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "Gateway",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "ownerReferences": [
                client.ApiClient().sanitize_for_serialization(owner)
            ]
        },
        "spec": {
            "gatewayClassName": "nginx",
            "listeners": [
                {
                    "protocol": "HTTP",
                    "name": "http-nginx",
                    "port": spec.get("port", 80),
                    "allowedRoutes": {
                        "namespaces": {
                            "from": "Same"
                        }
                    }
                }
            ]
        }
    }

def build_httproute(name: str, namespace: str, spec: dict, owner: V1OwnerReference) -> dict:
    return {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "HTTPRoute",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "ownerReferences": [
                client.ApiClient().sanitize_for_serialization(owner)
            ]
        },
        "spec": {
            "parentRefs": [
                {
                    "name": name,
                }
            ],
            "hostnames": [
                spec.get("domain")
            ],
            "rules": [
                {
                    "matches": [
                        {
                            "path": {
                                "type": "PathPrefix",
                                "value": "/"
                            }
                        }
                    ],
                    "backendRefs": [
                        {
                            "name": name,
                            "port": spec.get("port", 80),
                        }
                    ]
                }
            ]

        }
    }