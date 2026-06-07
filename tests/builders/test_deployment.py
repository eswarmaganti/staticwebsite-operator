from sw_operator.builders.deployment import build_deployment

class TestDeploymentMetadata:
    """
    The built deployment has the right name, namespace and labels etc
    """

    def test_name_matches_cr(self, deployment, base_spec):
        assert deployment.metadata.name == base_spec['metadata']['name']

    def test_namespace_matches_cr(self, deployment):
        assert deployment.metadata.namespace == "test"

    def test_managed_by_labels_is_set(self, deployment):
        labels = deployment.metadata.labels
        assert labels["app.kubernetes.io/managed-by"] == "staticwebsite-operator"

    def test_name_label_matches_cr(self, deployment, base_spec):
        assert deployment.metadata.labels["app.kubernetes.io/name"] == base_spec['metadata']['name']

    def test_owner_reference_is_attached(self, deployment, base_spec):
        assert len(deployment.metadata.owner_references) == 1

        owner_ref = deployment.metadata.owner_references[0]
        assert owner_ref.kind == "StaticWebsite"
        assert owner_ref.name == base_spec['metadata']['name']
        assert owner_ref.controller is True

class TestDeploymentSpec:
    """
    The Deployment spec reflects the CR spec correctly
    """
    def test_replica_count(self, deployment, base_spec):
        assert deployment.spec.replicas == base_spec['replicas']

    def test_replica_count_custom(self, base_spec, owner_reference):
        base_spec["replicas"] = 5
        deployment = build_deployment(
            name=base_spec['metadata']['name'],
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        assert deployment.spec.replicas == 5

    def test_container_image(self, deployment, base_spec):
        container=deployment.spec.template.spec.containers[0]
        assert container.image == base_spec['image']

    def test_container_ports(self,deployment, base_spec ):
        container=deployment.spec.template.spec.containers[0]
        assert container.ports[0].container_port == base_spec['targetPort']

    def test_container_name_matches_cr(self, deployment, base_spec):
        container=deployment.spec.template.spec.containers[0]
        assert container.name == base_spec['metadata']['name']

    def test_selector_matches_pod_labels(self, deployment):
        selector = deployment.spec.selector.match_labels
        pod_labels = deployment.spec.template.metadata.labels

        # Every selector key must present in pod labels with same value
        for key,value in selector.items():
            assert pod_labels.get(key) == value

class TestDeploymentResources:
    """
    Resource requests and limits are always set.
    """
    def test_resource_requests_is_set(self, deployment):
        resources=deployment.spec.template.spec.containers[0].resources
        assert resources.requests["cpu"] is not None
        assert resources.requests["memory"] is not None

    def test_resource_limits_is_set(self, deployment):
        resources=deployment.spec.template.spec.containers[0].resources
        assert resources.limits["cpu"] is not None
        assert resources.limits["memory"] is not None


class TestDeploymentProbes:
    """
    Liveness probe is set and listens on targetPort
    """
    def test_liveness_probe_is_set(self, deployment):
        assert deployment.spec.template.spec.containers[0].liveness_probe is not None

    def test_liveness_probe_matches_target_port(self, base_spec, owner_reference):
        base_spec["targetPort"]=8080
        deployment=build_deployment(
            name=base_spec['metadata']['name'],
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        probe = deployment.spec.template.spec.containers[0].liveness_probe
        assert probe.http_get.port == 8080