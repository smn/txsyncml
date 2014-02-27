# -*- test-case-name: txsyncml.tests.test_resource -*-

from twisted.web.resource import Resource


class TxSyncMLResource(Resource):

    def __init__(self, reactor):
        Resource.__init__(self)
        self.reactor = reactor
