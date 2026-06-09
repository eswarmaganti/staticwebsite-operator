import pytest
import kopf
from kubernetes.client.exceptions import ApiException
from unittest.mock import patch, MagicMock
from sw_operator.reconcilers.gateway import reconcile_gateway_resource, reconcile_httproute_resource, reconcile_gateway

class TestGatewayReconciler:
    """
    The test cases to test the gateway reconciler.
    """

    @patch('sw_operator.reconcilers.gateway.reconcile_gateway_resource')
    @patch('sw_operator.reconcilers.gateway.reconcile_httproute_resource')
    def test_mock_gateway_reconciler(self, mock_gateway, mock_httproute, base_spec, owner_reference, mock_logger):
        reconcile_gateway(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference,
            logger=mock_logger
        )
        mock_gateway.assert_called_once()
        mock_httproute.assert_called_once()

    @patch('sw_operator.reconcilers.gateway.custom_api')
    def test_create_gateway_when_not_exist(self, mock_custom_api, base_spec, owner_reference, mock_logger):
        """
        test the gateway reconciler for creating the gateway when not exist
        :param mock_custom_api:
        :param base_spec:
        :param owner_reference:
        :param mock_logger:
        :return:
        """
        mock_custom_api.create_namespaced_custom_object.return_value = MagicMock()

        reconcile_gateway_resource(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference,
            logger=mock_logger
        )

        mock_custom_api.create_namespaced_custom_object.assert_called_once()

        # assert the call_args
        call_args = mock_custom_api.create_namespaced_custom_object.call_args
        assert call_args[1]['namespace'] == 'test'

    @patch('sw_operator.reconcilers.gateway.custom_api')
    def test_create_httproute_when_not_exist(self, mock_custom_api, base_spec, owner_reference, mock_logger):
        """
        test the gateway reconciler for creating the httproute when not exist
        :param mock_custom_api:
        :param base_spec:
        :param owner_reference:
        :param mock_logger:
        :return:
        """
        mock_custom_api.create_namespaced_custom_object.return_value = MagicMock()
        reconcile_httproute_resource(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference,
            logger=mock_logger
        )
        mock_custom_api.create_namespaced_custom_object.assert_called_once()

        call_args = mock_custom_api.create_namespaced_custom_object.call_args
        assert call_args[1]['namespace'] == 'test'

    @patch('sw_operator.reconcilers.gateway.custom_api')
    def test_patch_gateway_when_exist(self, mock_custom_api, base_spec, owner_reference, mock_logger):
        """
        test the gateway reconciler for patching the gateway resource
        :param mock_custom_api:
        :param base_spec:
        :param owner_reference:
        :param mock_logger:
        :return:
        """
        mock_custom_api.create_namespaced_custom_object.side_effect = ApiException(409)
        mock_custom_api.patch_namespaced_custom_object.return_value = MagicMock()

        reconcile_gateway_resource(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference,
            logger=mock_logger
        )

        mock_custom_api.create_namespaced_custom_object.assert_called_once()

    @patch('sw_operator.reconcilers.gateway.custom_api')
    def test_patch_httproute_when_exist(self, mock_custom_api, base_spec, owner_reference, mock_logger):
        """
        test the gateway reconciler for patching the httproute resource
        :param mock_custom_api:
        :param base_spec:
        :param owner_reference:
        :param mock_logger:
        :return:
        """

        mock_custom_api.create_namespaced_custom_object.side_effect = ApiException(409)
        mock_custom_api.patch_namespaced_custom_object.return_value = MagicMock()

        reconcile_httproute_resource(
            name="portfolio",
            namespace="test",
            spec=base_spec,
            owner=owner_reference,
            logger=mock_logger
        )

        mock_custom_api.create_namespaced_custom_object.assert_called_once()

    @patch('sw_operator.reconcilers.gateway.custom_api')
    def test_gateway_resource_exception_handling(self, mock_custom_api, base_spec, owner_reference, mock_logger):
        mock_custom_api.create_namespaced_custom_object.side_effect = ApiException(500)

        with pytest.raises(kopf.TemporaryError):
            reconcile_gateway_resource(
                name="portfolio",
                namespace="test",
                spec=base_spec,
                owner=owner_reference,
                logger=mock_logger
            )

    @patch('sw_operator.reconcilers.gateway.custom_api')
    def test_httproute_resource_exception_handling(self, mock_custom_api, base_spec, owner_reference, mock_logger):
        mock_custom_api.create_namespaced_custom_object.side_effect = ApiException(500)

        with pytest.raises(kopf.TemporaryError):
            reconcile_httproute_resource(
                name="portfolio",
                namespace="test",
                spec=base_spec,
                owner=owner_reference,
                logger=mock_logger
            )
