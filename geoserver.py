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
import json


class GeoServer:
    def __init__(self):
        self.service_url = os.path.join(os.environ.get('GEOSERVER_URL'), 'geoserver')
        self.username = os.environ.get('GEOSERVER_USERNAME')
        self.password = os.environ.get('GEOSERVER_PASSWORD')

    def get_layers(self, workspace: str = None):
        """
        Get a list of layers.
        https://docs.geoserver.org/latest/en/api/#1.0.0/layers.yaml

        If workspace is None, it will list all the layers
        """
        url = "/layers" if workspace is None else f"/workspaces/{workspace}/layers"
        return self.get(url)

    def create_datastore(self, name: str, path: str, dbtype: str = 'geopkg',
                         workspace: str = None, overwrite: bool = False):
        """
        Create a data store.
        https://docs.geoserver.org/latest/en/api/#1.0.0/datastores.yaml

        name : Name of datastore to be created.
        path : Path to GeoPackage (.gpkg) file.
        """
        if workspace is None:
            workspace = "default"

        if path is None:
            raise Exception("You must provide a full path to the data")

        data = json.dumps({
            'dataStore': {
                'name': name,
                'connectionParameters': {
                    'database': f"file:{path}",
                    'dbtype': dbtype
                }
            }
        })

        try:
            self.post(f"/workspaces/{workspace}/datastores", data)

        except Exception as e:
            if overwrite:
                self.put(f"/workspaces/{workspace}/datastores/{name}", data)
            else:
                raise e

        return "Data store created/updated successfully"

    def get(self, route):
        r = requests.get(f"{self.service_url}/rest" + route, auth=(self.username, self.password))

        if r.status_code != 200:
            raise Exception(r.text)

        return r.text

    def post(self, route, data):
        headers = {"content-type": "application/json"}
        r = requests.post(f"{self.service_url}/rest" + route, data,
                          auth=(self.username, self.password), headers=headers)

        if r.status_code != 201:
            raise Exception(r.text)

    def put(self, route, data):
        headers = {"content-type": "application/json"}
        r = requests.put(f"{self.service_url}/rest" + route, data,
                         auth=(self.username, self.password), headers=headers)

        if r.status_code != 200:
            raise Exception(r.text)
