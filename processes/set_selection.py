import os

from subprocess import PIPE
from grass.pygrass.modules import Module

import pywps
from pywps import Process, ComplexInput, Format, LiteralOutput

from geoserver import GeoServer

geoserver = GeoServer()


class SetSelection(Process):
    def __init__(self):
        inputs = [
            ComplexInput('selection', 'Selection polygon',
                         supported_formats=[Format('application/json')])
        ]
        outputs = [
            LiteralOutput('center_east', 'Center coordinate (East)', data_type='float'),
            LiteralOutput('center_north', 'Center coordinate (North)', data_type='float')
        ]

        super(SetSelection, self).__init__(
            self._handler,
            identifier='set_selection',
            title="Set selection",
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        tmpdir = pywps.configuration.get_config_value("server", "tmpdir")
        datadir = os.path.join(
            pywps.configuration.get_config_value("server", "geoserverdir"), "data")

        infile = os.path.join(tmpdir, 'selection.json')

        with open(infile, 'w') as writer:
            writer.write(request.inputs['selection'][0].data)

        g_region = Module('g.region')
        g_remove = Module('g.remove')
        v_clip = Module('v.clip')
        v_import = Module('v.import')
        v_out_ogr = Module('v.out.ogr')

        g_remove(type='vector', name='selection', flags='f')

        v_import(input=infile, output='selection', overwrite=True)

        # Clip the basemaps by the selection map
        v_clip(input='points_osm', clip='selection', output='points', overwrite=True)
        v_clip(input='lines_osm', clip='selection', output='lines', overwrite=True)
        v_clip(input='polygons_osm', clip='selection', output='polygons', overwrite=True)

        # determine the center coordinate of the selection
        region = g_region(
            vector='selection', flags='cg', stdout_=PIPE).outputs.stdout.decode('utf-8')

        east, north = [float(s.split('=')[1]) for s in region.strip().split('\n')]

        # export GPKG files
        v_out_ogr(format='GPKG', input='selection', output=f"{datadir}/selection.gpkg",
                  overwrite=True)

        # create datastores in GeoServer
        geoserver.create_datastore(
            name="selection", path="data/selection.gpkg", workspace="vector", overwrite=True)

        # TODO: featurestores

        response.outputs['center_east'].data = east
        response.outputs['center_north'].data = north
        return response
