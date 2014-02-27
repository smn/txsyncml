# -*- test-case-name: txsyncml.tests.test_resource -*-

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.python import log
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET


class TxSyncMLResource(Resource):

    isLeaf = True

    def __init__(self, reactor):
        Resource.__init__(self)
        self.reactor = reactor

    def render_POST(self, request):

        def cb(request):
            request.write('ok')
            request.finish()

        d = Deferred()
        d.addCallback(cb)
        reactor.callLater(0, d.callback, request)
        return NOT_DONE_YET
