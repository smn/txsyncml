# -*- test-case-name: txsyncml.tests.test_resource -*-

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.python import log
from twisted.web.resource import Resource
from twisted.web import http
from twisted.web.server import NOT_DONE_YET

from txsyncml.codecs import get_codec
from txsyncml import constants
from txsyncml.commands import (
    SyncML, SyncHdr, SyncBody, Target, Source, Status)


class TxSyncMLError(Exception):

    def __init__(self, message, code):
        self.message = message
        self.code = code


class ContentTypeError(TxSyncMLError):
    def __init__(self, message='Unsupported content-type.'):
        super(ContentTypeError, self).__init__(message=message,
                                               code=http.NOT_ACCEPTABLE)


class TxSyncMLResource(Resource):

    isLeaf = True

    def __init__(self, reactor):
        Resource.__init__(self)
        self.reactor = reactor

    def render_POST(self, request):
        d = Deferred()
        d.addCallback(self.handle_request)
        d.addCallback(self.process_syncml, request)
        d.addCallback(self.finish_request, request)
        d.addErrback(self.handle_request_error, request)
        reactor.callLater(0, d.callback, request)
        return NOT_DONE_YET

    def handle_request_error(self, failure, request):
        error = failure.value
        if not failure.check(TxSyncMLError):
            log.err(failure)
            error = TxSyncMLError(message='Internal server error.')

        request.setHeader('Content-Type', 'text/plain')
        request.setResponseCode(error.code)
        request.write(error.message)
        request.finish()

    def get_codec(self, request):
        codec = get_codec(request)
        if codec is None:
            raise ContentTypeError()
        return codec

    def handle_request(self, request):
        codec = self.get_codec(request)
        return codec.decode(request.content.read())

    def process_syncml(self, syncml, request):
        codec = self.get_codec(request)

        header = SyncHdr(1, 1,
                         target=Target('target'),
                         source=Source('source'))
        body = SyncBody(
            statuses=[Status(cmd_id=1, msg_ref=1, cmd_ref=0, cmd='SyncHdr',
                             target_ref='http://www.syncml.org/sync-server',
                             source_ref='IMEI:493005100592800',
                             code=constants.AUTHENTICATION_ACCEPTED)])
        syncml = SyncML(header=header, body=body)
        return codec.encode(syncml.build().toXml())

    def finish_request(self, response, request):
        codec = self.get_codec(request)
        request.setHeader('Content-Type', codec.content_type)
        request.write(response)
        request.finish()
