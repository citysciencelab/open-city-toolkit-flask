import os

from pywps import Process, LiteralInput


class SetResolution(Process):
    def __init__(self):
        inputs = [
            LiteralInput('resolution', 'Resolution', data_type='float')
        ]

        super(SetResolution, self).__init__(
            self._handler,
            identifier='set_resolution',
            title="Set resolution",
            inputs=inputs
        )

    def _handler(self, request, response):
        resolution = request.inputs['resolution'][0].data
        outfile = os.path.join(os.environ.get('GRASS_DIR'), 'variables/resolution')

        with open(outfile, 'w') as writer:
            writer.write(str(resolution) + '\n')

        return response
