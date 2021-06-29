import os

from subprocess import PIPE
from grass.pygrass.modules import Module

import pywps
from pywps import Process, LiteralInput, LiteralOutput


class SetBasemap(Process):
    def __init__(self):
        inputs = [
            LiteralInput('filename', 'name of uploaded file', data_type='string')
        ]
        outputs = [
            LiteralOutput('center_east', 'Center coordinate (East)', data_type='float'),
            LiteralOutput('center_north', 'Center coordinate (North)', data_type='float')
        ]

        super(SetBasemap, self).__init__(
            self._handler,
            identifier='set_basemap',
            title="Set basemap",
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        tmpdir = pywps.configuration.get_config_value("server", "tmpdir")
        outputdir = pywps.configuration.get_config_value("server", "outputpath")

        infile = os.path.join(tmpdir, request.inputs['filename'][0].data)

        g_region = Module('g.region')
        v_in_ogr = Module('v.in.ogr')
        v_in_region = Module('v.in.region')
        v_out_ogr = Module('v.out.ogr')

        # import new basemap
        v_in_ogr(input=infile, layer='points', output='points_osm', overwrite=True)
        v_in_ogr(input=infile, layer='lines', output='lines_osm', overwrite=True)
        v_in_ogr(input=infile, layer='multipolygons', output='polygons_osm', overwrite=True)

        # determine the bbox and center coordinate from polygon layer boundary
        region = g_region(vector='polygons_osm', flags='cg', stdout_=PIPE).outputs.stdout.decode('utf-8')
        v_in_region(output='location_bbox', overwrite=True)

        east, north = [float(s.split('=')[1]) for s in region.strip().split('\n')]

        # export GPKG files
        v_out_ogr(format='GPKG', input='points_osm', output=os.path.join(outputdir, "points.gpkg"), overwrite=True)
        v_out_ogr(format='GPKG', input='lines_osm', output=os.path.join(outputdir, "lines.gpkg"), overwrite=True)
        v_out_ogr(format='GPKG', input='polygons_osm', output=os.path.join(outputdir, "polygons.gpkg"), overwrite=True)
        v_out_ogr(format='GPKG', input='location_bbox', output=os.path.join(outputdir, "location_bbox.gpkg"), overwrite=True)

        response.outputs['center_east'].data = east
        response.outputs['center_north'].data = north
        return response
