import kopf
from sw_operator.config import PLURAL, GROUP, VERSION
from sw_operator.reconcilers.staticwebsite import reconcile_staticwebsite

# decorator to handle the create events
@kopf.on.update(group=GROUP, version=VERSION, plural=PLURAL)
def update_staticwebsite(spec, name, namespace, patch, logger, body, **kwargs):

    reconcile_staticwebsite(
        name = name,
        namespace = namespace,
        spec = spec,
        body = body,
        patch = patch,
        logger = logger,
    )