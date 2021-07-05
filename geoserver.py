"""GeoServer API module. This script is based on modifications of the
"geoserver-rest" package.

MIT License

Copyright (c) 2021, Jan Behrens
Copyright (c) 2020, Geoinformatics Center, Asian Institute of Technology
Copyright (c) 2020, Tek Kshetri

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
import requests


class GeoServer:
    def __init__(self):
        self.service_url = os.path.join(os.environ.get('GEOSERVER_URL'), 'geoserver')
        self.username = os.environ.get('GEOSERVER_USERNAME')
        self.password = os.environ.get('GEOSERVER_PASSWORD')

    def create_datastore(self,
                         name: str,
                         path: str,
                         dbtype: str = 'geopkg',
                         workspace: str = None,
                         overwrite: bool = False):
        """
        Create a datastore within the GeoServer.

        Parameters
        ----------
        name : str
            Name of datastore to be created.
            After creating the datastore, you need to publish it by using publish_featurestore function.
        path : str
            Path to shapefile (.shp) file, GeoPackage (.gpkg) file, WFS url
            (e.g. http://localhost:8080/geoserver/wfs?request=GetCapabilities) or directory containing shapefiles.
        workspace : str, optional
        overwrite : bool

        Notes
        -----
        If you have PostGIS datastore, please use create_featurestore function
        """
        if workspace is None:
            workspace = "default"

        if path is None:
            raise Exception("You must provide a full path to the data")

        params = f"<database>file:{path}</database><dbtype>{dbtype}</dbtype>"
        data = f"<dataStore><name>{name}</name><connectionParameters>{params}</connectionParameters></dataStore>"

        try:
            self.post(f"{self.service_url}/rest/workspaces/{workspace}/datastores", data)

        except Exception as e:
            if overwrite:
                self.put(f"{self.service_url}/rest/workspaces/{workspace}/datastores/{name}", data)
            else:
                raise e

        return "Data store created/updated successfully"


    def post(self, url, data):
        headers = {"content-type": "text/xml"}
        r = requests.post(url, data, auth=(self.username, self.password), headers=headers)

        if r.status_code not in [200, 201]:
            raise Exception(r.text)


    def put(self, url, data):
        headers = {"content-type": "text/xml"}
        r = requests.put(url, data, auth=(self.username, self.password), headers=headers)

        if r.status_code not in [200, 201]:
            raise Exception(r.text)
