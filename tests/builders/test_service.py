from sw_operator.builders.service import build_service


class TestServiceMetadata:
    """
    Service Metadata must match with CR Spec
    """
    def test_service_name(self, service, base_spec):
        assert service.metadata.name == base_spec['metadata']['name']

    def test_service_namespace(self, service):
        assert service.metadata.namespace == "test"

    def test_service_managed_by_labels_set(self, service):

        assert service.metadata.labels["app.kubernetes.io/managed-by"] == "staticwebsite-operator"

    def test_service_owner_ref_attached(self, service,  base_spec):

        assert len(service.metadata.owner_references) == 1
        owner_ref = service.metadata.owner_references[0]
        assert owner_ref.kind == "StaticWebsite"
        assert owner_ref.name == base_spec['metadata']['name']
        assert owner_ref.controller is True

    def test_service_name_label_matches_cr(self, service, base_spec):
        assert service.metadata.labels["app.kubernetes.io/name"] == base_spec['metadata']['name']

class TestServiceSpec:
    """
    Service Spec must match with CR Spec
    """

    def test_service_type(self, service, base_spec):

        assert service.spec.type == 'NodePort'

    def test_service_ports(self, service, base_spec):
        ports = service.spec.ports[0]
        assert ports.port == base_spec['port']
        assert ports.target_port == base_spec['targetPort']

    def test_service_selector(self, service, base_spec):

        selector = service.spec.selector
        assert selector["app.kubernetes.io/name"] == base_spec['metadata']['name']
        assert selector["app.kubernetes.io/managed-by"] == "staticwebsite-operator"