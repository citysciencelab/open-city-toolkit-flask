import os

from subprocess import PIPE
from grass.pygrass.modules import Module

import pywps
from pywps import Process, LiteralInput, LiteralOutput

from geoserver import GeoServer

geoserver = GeoServer()


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
        datadir = os.path.join(
            pywps.configuration.get_config_value("server", "geoserverdir"), "data")

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
        region = g_region(vector='polygons_osm', flags='cg', stdout_=PIPE).outputs.stdout
        v_in_region(output='location_bbox', overwrite=True)

        east, north = [float(s.split('=')[1]) for s in region.strip().split('\n')]

        # export GPKG files
        v_out_ogr(format='GPKG', input='points_osm', output=f"{datadir}/points.gpkg",
                  overwrite=True)
        v_out_ogr(format='GPKG', input='lines_osm', output=f"{datadir}/lines.gpkg",
                  overwrite=True)
        v_out_ogr(format='GPKG', input='polygons_osm', output=f"{datadir}/polygons.gpkg",
                  overwrite=True)
        v_out_ogr(format='GPKG', input='location_bbox', output=f"{datadir}/location_bbox.gpkg",
                  overwrite=True)

        # create datastores in GeoServer
        geoserver.create_datastore(
            name="basemap_points", path="data/points.gpkg", workspace="vector", overwrite=True)
        geoserver.create_datastore(
            name="basemap_lines", path="data/lines.gpkg", workspace="vector", overwrite=True)
        geoserver.create_datastore(
            name="basemap_polygons", path="data/polygons.gpkg", workspace="vector", overwrite=True)
        geoserver.create_datastore(
            name="basemap_bbox", path="data/location_bbox.gpkg", workspace="vector",
            overwrite=True)

        # TODO: featurestores

        response.outputs['center_east'].data = east
        response.outputs['center_north'].data = north
        return response
