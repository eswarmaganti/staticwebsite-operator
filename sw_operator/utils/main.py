
# function to identify the patch needed for deployment
def deployment_needs_reconciliation(current, desired):
    current_container = current.spec.template.spec.containers[0]
    desired_container = desired.spec.template.spec.containers[0]

    return any([
        current.spec.replicas != desired.spec.replicas,

        current_container.image != desired_container.image,

        current_container.ports[0].container_port != desired_container.ports[0].container_port,

        current.spec.selector.match_labels != desired.spec.selector.match_labels,
    ])


# function to identify the patch needed for service
def service_needs_reconciliation(current, desired):
    current_port = current.spec.ports[0]
    desired_port = desired.spec.ports[0]


    return any([
        current_port.port != desired_port.port,

        current_port.target_port != desired_port.target_port,

        current.spec.selector != desired.spec.selector,

        current.spec.type != desired.spec.type,
    ])

# function to identify the reconciliation needed for GW API resources
def gateway_needs_reconciliation(current, desired) -> bool:
    pass