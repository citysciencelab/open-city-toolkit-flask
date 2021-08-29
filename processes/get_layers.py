from pywps import Process, LiteralOutput

from geoserver import GeoServer

geoserver = GeoServer()


class GetLayers(Process):
    def __init__(self):
        outputs = [
            LiteralOutput('response', 'Output response', data_type='string')
        ]

        super(GetLayers, self).__init__(
            self._handler,
            identifier='get_layers',
            title='Get Layers',
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        response.outputs['response'].data = geoserver.get_layers()
        return response
