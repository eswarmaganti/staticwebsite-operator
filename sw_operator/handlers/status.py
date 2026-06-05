import kopf
from sw_operator.reconcilers.status import reconcile_status
# the status handling decorator
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