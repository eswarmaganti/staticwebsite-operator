import pytest
from unittest.mock import MagicMock, patch
from sw_operator.reconcilers.service import reconcile_service
from kubernetes.client.exceptions import ApiException
import kopf

class TestServiceReconciler:
    """
    Unit tests for sw_operator.reconcilers.service
    """

    @patch("sw_operator.reconcilers.service.core_v1")
    def test_creates_service_when_not_exists(self, mock_core_v1, base_spec, owner_reference, mock_logger ):
        """
        Method to test the service creation reconciler logic
        :param mock_core_v1:
        :param base_spec:
        :param owner_reference:
        :param mock_logger:
        :return:
        """

        mock_core_v1.create_namespaced_service.return_value = MagicMock()

        reconcile_service(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference,
            logger=mock_logger
        )

        # assert the create_namespaced_service is called or not
        mock_core_v1.create_namespaced_service.assert_called_once()

        # assert the parameters of create_namespaced_service
        call_args = mock_core_v1.create_namespaced_service.call_args
        assert call_args[1]['namespace'] == 'test'

    @patch("sw_operator.reconcilers.service.core_v1")
    def test_patch_service_when_exists(self, mock_core_v1, base_spec, owner_reference, mock_logger ):
        """
        method to test the reconciler logic when invoked to patch the existing service
        :param mock_core_v1:
        :param base_spec:
        :param owner_reference:
        :param mock_logger:
        :return:
        """

        # simulate the 409 exception for existing service
        mock_core_v1.create_namespaced_service.side_effect = ApiException(409)
        mock_core_v1.patch_namespaced_service.return_value = MagicMock()

        # invoke the reconcile function
        reconcile_service(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference,
            logger=mock_logger
        )

        # assert the patch_namespaced_service
        mock_core_v1.patch_namespaced_service.assert_called_once()

    @patch("sw_operator.reconcilers.service.core_v1")
    def test_service_exception_handling(self,mock_core_v1, base_spec, owner_reference, mock_logger ):
        """
        Method to test the exception handling when TemporaryError is raised
        :param mock_core_v1:
        :param base_spec:
        :param owner_reference:
        :param mock_logger:
        :return:
        """

        # simulate the 500 exception
        mock_core_v1.create_namespaced_service.side_effect = ApiException(500)

        with pytest.raises(kopf.TemporaryError):
            reconcile_service(
                name="portfolio",
                namespace="test",
                spec=base_spec,
                owner=owner_reference,
                logger=mock_logger
            )