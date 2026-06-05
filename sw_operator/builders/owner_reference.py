from sw_operator.clients.kubernetes import client

# utility function to build an owner reference for kubernetes objects
def build_owner_reference(body):
    return client.V1OwnerReference(
        api_version=body.get('apiVersion'),
        kind=body.get('kind'),
        name=body.get('metadata').get('name'),
        uid=body.get('metadata').get('uid'),
        controller=True,
        block_owner_deletion=True
    )
