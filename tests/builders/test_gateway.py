
# test cases for Gateway resource
class TestGatewayMetadata:
    """
    Gateway Metadata must match with CR Spec
    """
    def test_gateway_name(self, gateway):
        assert gateway['metadata']['name'] == "portfolio"

    def test_gateway_namespace(self, gateway):
        assert gateway['metadata']['namespace'] == "test"

    def test_gateway_name_label_matches_cr(self, gateway):
        assert gateway['metadata']['labels']['app.kubernetes.io/name'] == "portfolio"
    def test_gateway_managed_by_labels_set(self, gateway):
        assert gateway['metadata']['labels']['app.kubernetes.io/managed-by'] == "staticwebsite-operator"

    def test_gateway_owner_ref_is_set(self, gateway, base_spec):
        assert len(gateway['metadata']['ownerReferences']) == 1
        owner_ref = gateway['metadata']['ownerReferences'][0]
        assert owner_ref['kind'] == 'StaticWebsite'
        assert owner_ref['name'] == base_spec['metadata']['name']
        assert owner_ref['controller'] is True

class TestGatewaySpec:
    """
    Gateway Spec must be valid & match with CR Spec
    """
    def test_gateway_class_name(self, gateway, ):
        assert gateway['spec']['gatewayClassName'] == 'nginx'

    def test_gateway_listeners(self, gateway, base_spec):
        listeners = gateway['spec']['listeners'][0]
        assert listeners['port'] == base_spec['port']
        assert listeners['protocol'] == 'HTTP'


# test cases for HTTPRoute resource
class TestHTTPRouteMetadata:
    """
    HTTPRoute Metadata must match with CR Spec
    """
    def test_httproute_name(self, httproute):
        assert httproute['metadata']['name'] == "portfolio"

    def test_httproute_namespace(self, httproute):
        assert httproute['metadata']['namespace'] == "test"

    def test_httproute_name_label_matches_cr(self, httproute):
        assert httproute['metadata']['labels']['app.kubernetes.io/name'] == "portfolio"
    def test_httproute_managed_by_labels_set(self, httproute):
        assert httproute['metadata']['labels']['app.kubernetes.io/managed-by'] == "staticwebsite-operator"

    def test_httproute_owner_ref_is_set(self, httproute, base_spec):
        assert len(httproute['metadata']['ownerReferences']) == 1
        owner_ref = httproute['metadata']['ownerReferences'][0]
        assert owner_ref['kind'] == 'StaticWebsite'
        assert owner_ref['name'] == base_spec['metadata']['name']
        assert owner_ref['controller'] is True

class TestHTTPRouteSpec:
    """
    HTTPRoute Spec must be valid & match with CR Spec
    """
    def test_httproute_parent_refs(self, httproute, base_spec):

        assert len(httproute['spec']['parentRefs']) == 1
        assert httproute['spec']['parentRefs'][0]['name'] == base_spec['metadata']['name']

    def test_httproute_hostnames(self, httproute, base_spec):
        assert len(httproute['spec']['hostnames']) == 1
        assert httproute['spec']['hostnames'][0] == base_spec['domain']

    def test_httproute_backendrefs(self, httproute, base_spec):
        rules = httproute['spec']['rules']

        assert len(rules) == 1
        assert len(rules[0]['backendRefs']) == 1

        backend_ref = rules[0]['backendRefs'][0]
        # backendRef must match the service name and port
        assert backend_ref['name'] == base_spec['metadata']['name']
        assert backend_ref['port'] == base_spec['port']