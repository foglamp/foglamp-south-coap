# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

from unittest.mock import patch
import pytest

from python.foglamp.plugins.south.coap import coap

__author__ = "Praveen Garg"
__copyright__ = "Copyright (c) 2017 OSIsoft, LLC"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

config = coap._DEFAULT_CONFIG


def test_plugin_contract():
    # Evaluates if the plugin has all the required methods
    assert callable(getattr(coap, 'plugin_info'))
    assert callable(getattr(coap, 'plugin_init'))
    assert callable(getattr(coap, 'plugin_start'))
    assert callable(getattr(coap, 'plugin_shutdown'))
    assert callable(getattr(coap, 'plugin_reconfigure'))


def test_plugin_info():
    assert coap.plugin_info() == {
        'name': 'CoAP Plugin',
        'version': '1.0',
        'mode': 'async',
        'type': 'south',
        'interface': '1.0',
        'config': config
    }


def test_plugin_init():
    assert coap.plugin_init(config) == config


@pytest.mark.skip(reason="To be implemented")
def test_plugin_start():
    pass


@pytest.mark.skip(reason="To be implemented")
def test_plugin_reconfigure():
    pass


def test__plugin_stop():
    with patch.object(coap._LOGGER, 'info') as patch_logger_info:
        coap._plugin_stop(config)
    patch_logger_info.assert_called_once_with('CoAP disconnected.')


def test_plugin_shutdown():
    with patch.object(coap, "_plugin_stop", return_value="") as patch_stop:
        with patch.object(coap._LOGGER, 'info') as patch_logger_info:
            coap.plugin_shutdown(config)
        patch_logger_info.assert_called_once_with('CoAP plugin shut down.')
    patch_stop.assert_called_once_with(config)
