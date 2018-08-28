# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

"""CoAP handler for sensor readings"""

import asyncio
import copy
import logging

import aiocoap.resource
import aiocoap.error
import cbor2

from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south.ingest import Ingest

__author__ = "Terris Linenbach"
__copyright__ = "Copyright (c) 2017 OSIsoft, LLC"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_LOGGER = logger.setup(__name__)
# We want to see informational output from this plugin
_LOGGER.setLevel(logging.INFO)

_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'CoAP Listener South Plugin',
        'type': 'string',
        'default': 'coap',
        'readonly': 'true'
    },
    'port': {
        'description': 'Port to listen on',
        'type': 'integer',
        'default': '5683',
        'order': '1'
    },
    'uri': {
        'description': 'URI to accept data on',
        'type': 'string',
        'default': 'sensor-values',
        'order': '2'
    }
}

aiocoap_ctx = None
_task = None


def plugin_info():
    """ Returns information about the plugin.

    Args:
    Returns:
        dict: plugin information
    Raises:
    """

    return {'name': 'CoAP Plugin',
            'version': '1.0',
            'mode': 'async',
            'type': 'south',
            'interface': '1.0',
            'config': _DEFAULT_CONFIG
            }


def plugin_init(config):
    """ Registers CoAP handler to accept sensor readings

    Args:
        config: JSON configuration document for the South plugin configuration category
    Returns:
        handle: JSON object to be used in future calls to the plugin
    Raises:
    """
    handle = config
    return handle


def plugin_start(handle):
    """ Starts the South service ingress process.
        Used only for plugins that support async IO.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    global _task

    uri = handle['uri']['value']
    port = handle['port']['value']
    try:
        _task = asyncio.ensure_future(_start_aiocoap(uri, port))
    except asyncio.CancelledError:
        pass


async def _start_aiocoap(uri, port):
    root = aiocoap.resource.Site()

    root.add_resource(('.well-known', 'core'),
                      aiocoap.resource.WKCResource(root.get_resources_as_linkheader))

    root.add_resource(('other', uri), CoAPIngest())

    global aiocoap_ctx
    aiocoap_ctx = await aiocoap.Context().create_server_context(root, bind=('::', int(port)))
    _LOGGER.info('CoAP listener started on port {} with uri {}'.format(port, uri))


def plugin_reconfigure(handle, new_config):
    """  Reconfigures the plugin

    it should be called when the configuration of the plugin is changed during the operation of the South service;
    The new configuration category should be passed.

    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    Raises:
    """
    _LOGGER.info("Old config for CoAP plugin {} \n new config {}".format(handle, new_config))

    # Find diff between old config and new config
    diff = utils.get_diff(handle, new_config)

    # Plugin should re-initialize and restart if key configuration is changed
    if 'port' in diff or 'uri' in diff:
        plugin_shutdown(handle)
        new_handle = plugin_init(new_config)
        new_handle['restart'] = 'yes'
        _LOGGER.info("Restarting CoAP plugin due to change in configuration keys [{}]".format(', '.join(diff)))
    else:
        new_handle = copy.deepcopy(new_config)
        new_handle['restart'] = 'no'
    return new_handle


def _plugin_stop(handle):
    _LOGGER.info('Stopping South CoAP plugin...')
    try:
        asyncio.ensure_future(aiocoap_ctx.shutdown())
    except Exception as ex:
        _LOGGER.exception('Error in shutting down CoAP plugin {}'.format(str(ex)))
        raise


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup, to be called prior to the South service being shut down.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    global _task
    if _task is not None:
        _task.cancel()
        _task = None

    _plugin_stop(handle)
    _LOGGER.info('CoAP plugin shut down.')


class CoAPIngest(aiocoap.resource.Resource):
    """Handles incoming sensor readings from CoAP"""

    @staticmethod
    async def render_post(request):
        """Store sensor readings from CoAP to FogLAMP

        Args:
            request:
                The payload is a cbor-encoded array that decodes to JSON
                similar to the following:

                .. code-block:: python

                    {
                        "timestamp": "2017-01-02T01:02:03.23232Z-05:00",
                        "asset": "pump1",
                        "key": "80a43623-ebe5-40d6-8d80-3f892da9b3b4",
                        "readings": {
                            "velocity": "500",
                            "temperature": {
                                "value": "32",
                                "unit": "kelvin"
                            }
                        }
                    }
        """
        # aiocoap handlers must be defensive about exceptions. If an exception
        # is raised out of a handler, it is permanently disabled by aiocoap.
        # Therefore, Exception is caught instead of specific exceptions.

        code = aiocoap.numbers.codes.Code.VALID
        message = ''
        try:
            if not Ingest.is_available():
                message = '{"busy": true}'
                raise aiocoap.error.CommunicationKilled(message)

            try:
                payload = cbor2.loads(request.payload)
            except Exception:
                raise ValueError('Payload must be a dictionary')

            asset = payload['asset']
            timestamp = payload['timestamp']
            key = payload['key']

            # readings or sensor_values are optional
            try:
                readings = payload['readings']
            except KeyError:
                readings = payload['sensor_values']  # sensor_values is deprecated

            # if optional then
            # TODO: confirm, do we want to check this?
            if not isinstance(readings, dict):
                raise ValueError('readings must be a dictionary')

            await Ingest.add_readings(asset=asset, timestamp=timestamp, key=key, readings=readings)

        except (KeyError, ValueError, TypeError) as e:
            Ingest.increment_discarded_readings()
            _LOGGER.exception("%d: %s", aiocoap.numbers.codes.Code.BAD_REQUEST, str(e))
            raise aiocoap.error.BadRequest(str(e))
        except Exception as ex:
            Ingest.increment_discarded_readings()
            _LOGGER.exception("%d: %s", aiocoap.numbers.codes.Code.INTERNAL_SERVER_ERROR, str(ex))
            raise aiocoap.error.ConstructionRenderableError(str(ex))

        return aiocoap.Message(payload=message.encode('utf-8'), code=code)
