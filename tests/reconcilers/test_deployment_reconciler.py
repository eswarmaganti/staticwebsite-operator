import pytest
from unittest.mock import MagicMock, patch
from kubernetes.client import ApiException
import kopf

from sw_operator.reconcilers.deployment import reconcile_deployment


class TestReconcileDeploymentCreate():

    @patch("sw_operator.reconcilers.deployment.AppsV1Api")
    def test_creates_deployment_when_not_exists(self, mock_api, base_spec, owner_reference, mock_logger):
        # setting the return value for create_namespace_deployment method
        api = mock_api()
        api.create_namespaced_deployment.return_value = MagicMock()

        # invoking the reconcile_deployment for deployment creation scenario
        reconcile_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference,
            logger=mock_logger
        )

        # asserting the create_namespace_deployment method
        api.create_namespaced_deployment.assert_called_once()

        # asserting the first positional argument passed to create_namespaced_deployment method
        call_args = api.create_namespaced_deployment.call_args

        assert call_args[1]['namespace'] == "test" # namespace

    @patch("sw_operator.reconcilers.deployment.AppsV1Api")
    def test_patch_deployment_when_exists(self, mock_api, base_spec, owner_reference, mock_logger):
        api = mock_api()

        # simulate 409 conflict on create -- deployment already exists
        api.create_namespaced_deployment.side_effect = ApiException(status=409)

        # setting up the return value of the patch_namespaced_deployment
        api.patch_namespaced_deployment.return_value = MagicMock()

        reconcile_deployment(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference,
            logger=mock_logger
        )

        # asserting the patch_namespaced_deployment
        api.patch_namespaced_deployment.assert_called_once()

    @patch("sw_operator.reconcilers.deployment.AppsV1Api")
    def test_raises_temporary_error_on_api_failure(self, mock_api, base_spec, owner_reference, mock_logger):
        """
        Method to test the failure case for exception other than 409
        :param mock_api:
        :param base_spec:
        :param owner_reference:
        :param mock_logger:
        :return:
        """
        api = mock_api()

        # simulating the 500 exception
        api.create_namespaced_deployment.side_effect = ApiException(status=500)

        # asserting the reconcile_deployment to catch 500 exception
        with pytest.raises(kopf.TemporaryError):
            reconcile_deployment(
                name="portfolio",
                namespace="test",
                spec=base_spec,
                owner=owner_reference,
                logger=mock_logger
            )