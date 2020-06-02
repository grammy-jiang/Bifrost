from bifrost.service import Service


class BifrostService(Service):
    def __init__(self, settings):
        super(BifrostService, self).__init__(settings)
