import kopf
from sw_operator.config import PLURAL, GROUP, VERSION
from sw_operator.reconcilers.staticwebsite import reconcile_staticwebsite
from sw_operator.reconcilers.status import reconcile_status


# decorator to handle the create, update and resume events for StaticWebsite CustomResource
@kopf.on.resume(group=GROUP, version=VERSION, plural=PLURAL)
@kopf.on.create(group=GROUP, version=VERSION, plural=PLURAL)
@kopf.on.update(group=GROUP, version=VERSION, plural=PLURAL)
def create_staticwebsite(spec, name, namespace, patch, logger, body, **kwargs):

    reconcile_staticwebsite(
        name=name,
        namespace=namespace,
        spec=spec,
        body=body,
        patch=patch,
        logger=logger,
    )

# decorator to handle the delete event
@kopf.on.delete(group=GROUP, version=VERSION, plural=PLURAL)
def handle_delete_event(name, **kwargs):
    print(f"The Custom Resource {name} is deleted")


# Decorator to reconcile the status of the StaticWebsite CustomResource
@kopf.on.field(
    group='apps',
    version='v1',
    plural='deployments',
    field='status.availableReplicas',
    labels={'app.kubernetes.io/managed-by': 'staticwebsite-operator'},
)
def status(name, namespace, body, logger, **kwargs):
    reconcile_status(
        name=name,
        namespace=namespace,
        body=body,
        logger=logger,
    )