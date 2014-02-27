# -*- test-case-name: txsyncml.tests.test_resource -*-

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.python import log
from twisted.web.resource import Resource
from twisted.web import http
from twisted.web.server import NOT_DONE_YET


class TxSyncMLError(Exception):

    def __init__(self, message, code):
        self.message = message
        self.code = code


class ContentTypeError(TxSyncMLError):
    def __init__(self, content_type):
        super(ContentTypeError, self).__init__(
            message='This server cannot accept content type: %s' % (
                content_type,),
            code=http.NOT_ACCEPTABLE)


class TxSyncMLResource(Resource):

    timeout = 1
    isLeaf = True

    def __init__(self, reactor):
        Resource.__init__(self)
        self.reactor = reactor

    def render_POST(self, request):
        d = Deferred()
        d.addCallback(self.handle_request)
        d.addErrback(self.handle_request_error, request)
        reactor.callLater(0, d.callback, request)
        return NOT_DONE_YET

    def handle_request(self, request):
        content_type_parser = {
            'application/vnd.syncml+xml': self.parse_xml,
        }

        # NOTE: I'm ignoring content-type in the format
        #       'application/json; charset=utf-8'. Burn that bridge when
        #       I get there.
        [content_type] = request.requestHeaders.getRawHeaders('Content-Type')
        parser = content_type_parser.get(content_type)
        if parser is None:
            raise ContentTypeError(content_type)

        print 'parser', parser

        request.write('ok')
        request.finish()

    def handle_request_error(self, failure, request):
        error = failure.value
        if not failure.check(TxSyncMLError):
            log.err(failure)
            error = TxSyncMLError(message='Internal server error.')

        request.setHeader('Content-Type', 'application/vnd.syncml+xml')
        request.setResponseCode(error.code)
        request.write(error.message)
        request.finish()

    def parse_xml(self, request):
        return request
