# shared fixtures for all tests
import pytest
from unittest.mock import MagicMock, patch

# patch the kubernetes config loaders before any sw_operator module is imported
# this prevents "No configuration found" errors in CI where no kubernetes cluster exists

patch("kubernetes.config.load_kube_config", return_value=None).start()
patch("kubernetes.config.load_incluster_config", return_value=None).start()

# importing the builder methods after patching the kube_config to avoid runtime error to load kube config
from sw_operator.builders.gateway import build_gateway, build_httproute
from sw_operator.builders.service import build_service
from sw_operator.builders.deployment import build_deployment

@pytest.fixture
def base_spec() -> dict:
    """
    Minimal Valid StaticWebsite specification
    :return: dict
    """
    return {
        "metadata": {
            "name": "portfolio",
        },
        "image": "nginx:1.31-alpine",
        "replicas": 2,
        "port": 80,
        "targetPort": 80,
        "domain": "portfolio.eswar.dev"
    }

@pytest.fixture
def owner_reference():
    """
    Fake owner reference as the builder receives it.
    :return: object
    """
    from kubernetes import client as k8s
    return k8s.V1OwnerReference(
        api_version="platform.eswar.dev",
        kind="StaticWebsite",
        name="portfolio",
        uid="8c68956a-c201-47b4-b191-c2ca567ea0e4",
        controller=True,
        block_owner_deletion=True,
    )

@pytest.fixture
def deployment(base_spec, owner_reference):
    return build_deployment(
        name="portfolio",
        namespace="test",
        spec=base_spec,
        owner=owner_reference,
    )

@pytest.fixture
def gateway(base_spec, owner_reference):
    """
    Build gateway object
    :param base_spec:
    :param owner_reference:
    :return:
    """
    return build_gateway(
        name="portfolio",
        namespace="test",
        spec=base_spec,
        owner=owner_reference,
    )
@pytest.fixture
def httproute(base_spec, owner_reference):
    """
    Build httproute object
    :param base_spec:
    :param owner_reference:
    :return:
    """
    return build_httproute(
        name="portfolio",
        namespace="test",
        spec=base_spec,
        owner=owner_reference,
    )

@pytest.fixture
def service(base_spec, owner_reference):
    """
    Build service object
    :param base_spec:
    :param owner_reference:
    :return:
    """
    return build_service(
        name="portfolio",
        namespace="test",
        spec=base_spec,
        owner=owner_reference,
    )