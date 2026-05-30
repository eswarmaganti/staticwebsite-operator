from email.base64mime import body_decode

import kopf
from kubernetes import client, config
from kubernetes.client import ApiException

# Load the kube-config
config.load_kube_config()

apps_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()

# utility function to create the deployment specification
def build_deployment(spec, name, owner):
    return client.V1Deployment(
        metadata = client.V1ObjectMeta(
            name = name,
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
                                  container_port=spec.get('port'),
                              )
                          ]
                      )
                  ]
                )
            )
        )
    )

# utility function to build an owner reference for kubernetes objects
def build_owner_reference(body):
    return client.V1OwnerReference(
        api_version = body.get('apiVersion'),
        kind = body.get('kind'),
        name = body.get('metadata').get('name'),
        uid = body.get('metadata').get('uid'),
        controller = True,
        block_owner_deletion = True
    )


# utility function to build the service manifest
def build_service(name, spec, owner):
    return client.V1Service(
        metadata = client.V1ObjectMeta(
            name = name,
        ),
        spec = client.V1ServiceSpec(
            selector = client.V1LabelSelector(
                match_labels = {"app": name},
            ),
            ports = client.V1ServicePort(
                port = spec.get('port'),
                target_port = spec.get('targetPort'),
            )
        )
    )

@kopf.on.create('platform.eswar.dev', 'v1alpha1', 'staticwebsites')
def create_staticwebsite(spec, name, namespace, patch, logger, body, **kwargs):
    # build the owner reference
    owner = build_owner_reference(body)

    logger.info(f"Creating website: {name}")

    # creating the deployment specification
    deployment = build_deployment(name, spec, owner)

    try:
        apps_v1.read_namespaced_deployment(
            name=name,
            namespace=namespace,
        )
        logger.info(f"Deployment Exists: {name}")
    except ApiException as e:
        # Creating the deployment
        if e.status == 404:
            apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=deployment
            )
            logger.info(f"Deployment Created: {name}")

    # defining the service specification
    service = build_service(name, spec, owner)

    try:
        core_v1.read_namespaced_service(
            name=name,
            namespace=namespace
        )
        logger.info(f"Service Exists: {name}")
    except  ApiException as e:
        # Create the service
        if e.status == 404:
            core_v1.create_namespaced_service(
                namespace=namespace,
                body=service
            )

            logger.info(f"Service Created: {name}")

    patch.status['phase'] = "Running"
    patch.status['deploymentName'] = name
    patch.status['serviceName'] = name


# handling the update actions on the CR
@kopf.on.update('paltform.eswar.dev', 'v1alpha1', 'staticwebsites')
def update_staticwebsite(spec, name, namespace, patch, logger, body, **kwargs):
    owner = build_owner_reference(body),

    # Creating the desired deployment and patching the updates
    desired_deployment = build_deployment(name, spec, owner)
    logger.info(f"Updating website: {name}")

    apps_v1.patch_namespaced_deployment(
        name=name,
        namespace=namespace,
        body=desired_deployment
    )

    # Creating a desired service and patching the updates
    desired_service = build_service(name, spec, owner)
    logger.info(f"Updating service: {name}")
    core_v1.patch_namespaced_service(
        name=name,
        namespace=namespace,
        body=desired_service
    )

    patch.status['phase'] = "Running"
    patch.status['deploymentName'] = name
    patch.status['serviceName'] = name