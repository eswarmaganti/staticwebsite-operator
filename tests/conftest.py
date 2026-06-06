# shared fixtures for all tests
import pytest

@pytest.fixture
def base_spec() -> dict:
    """
    Minimal Valid StaticWebsite specification
    :return: dict
    """
    return {
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