import pytest
from kubernetes import client as k8s
from sw_operator.builders.deployment import build_deployment

class TestDeploymentMetadata:
    """
    The built deployment has the right name, namespace and labels etc
    """

    def test_name_matches_cr(self, base_spec, owner_reference):
        dep = build_deployment(
            name="portfolio",
            spec=base_spec,
            namespace="test",
            owner=owner_reference
        )
        assert dep.metadata.name == "portfolio"

    def test_namespace_matches_cr(self, base_spec, owner_reference):
        dep = build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        assert dep.metadata.namespace == "test"

    def test_managed_by_labels_is_set(self, base_spec, owner_reference):
        dep = build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        labels = dep.metadata.labels
        assert labels["app.kubernetes.io/managed-by"] == "staticwebsite-operator"

    def test_name_label_matches_cr(self, base_spec, owner_reference):
        dep = build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        assert dep.metadata.labels["app.kubernetes.io/name"] == "portfolio"

    def test_owner_reference_is_attached(self, base_spec, owner_reference):
        dep = build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        assert len(dep.metadata.owner_references) == 1

        owner_ref = dep.metadata.owner_references[0]
        assert owner_ref.kind == "StaticWebsite"
        assert owner_ref.name == "portfolio"
        assert owner_ref.controller is True

class TestDeploymentSpec:
    """
    The Deployment spec reflects the CR spec correctly
    """
    def test_replica_count(self, base_spec, owner_reference):
        dep = build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        assert dep.spec.replicas == 2

    def test_replica_count_custom(self, base_spec, owner_reference):
        base_spec["replicas"] = 5
        dep = build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        assert dep.spec.replicas == 5

    def test_container_image(self, base_spec, owner_reference):
        dep = build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        container=dep.spec.template.spec.containers[0]
        assert container.image == "nginx:1.31-alpine"

    def test_container_ports(self,base_spec, owner_reference ):
        dep=build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        container=dep.spec.template.spec.containers[0]
        assert container.ports[0].container_port == 80

    def test_container_name_matches_cr(self, base_spec, owner_reference):
        dep = build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        container=dep.spec.template.spec.containers[0]
        assert container.name == "portfolio"

    def test_selector_matches_pod_labels(self, base_spec, owner_reference):
        dep = build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        selector = dep.spec.selector.match_labels
        pod_labels = dep.spec.template.metadata.labels

        # Every selector key must present in pod labels with same value
        for key,value in selector.items():
            assert pod_labels.get(key) == value

class TestDeploymentResources:
    """
    Resource requests and limits are always set.
    """
    def test_resource_requests_is_set(self, base_spec, owner_reference):
        dep = build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        resources=dep.spec.template.spec.containers[0].resources
        assert resources.requests["cpu"] is not None
        assert resources.requests["memory"] is not None

    def test_resource_limits_is_set(self, base_spec, owner_reference):
        dep = build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        resources=dep.spec.template.spec.containers[0].resources
        assert resources.limits["cpu"] is not None
        assert resources.limits["memory"] is not None


class TestDeploymentProbes:
    """
    Liveness probe is set and listens on targetPort
    """
    def test_liveness_probe_is_set(self, base_spec, owner_reference):
        dep = build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        assert dep.spec.template.spec.containers[0].liveness_probe is not None

    def test_liveness_probe_matches_target_port(self, base_spec, owner_reference):
        base_spec["targetPort"]=8080
        dep = build_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference
        )
        probe = dep.spec.template.spec.containers[0].liveness_probe
        assert probe.http_get.port == 8080