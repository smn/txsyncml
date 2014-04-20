# -*- test-case-name: txsyncml.tests.test_resource -*-
from xml.dom import minidom

from twisted.internet.defer import maybeDeferred
from twisted.python import log
from twisted.web.resource import Resource
from twisted.web import http
from twisted.web.server import NOT_DONE_YET

from txsyncml.codecs import get_codec
from txsyncml import constants
from txsyncml.commands import (
    SyncML, SyncHdr, SyncBody, Target, Source, Status, Chal)
from txsyncml.parser import SyncMLParser
from txsyncml.syncml import AuthenticationBackend


class TxSyncMLError(Exception):

    def __init__(self, message, code=http.INTERNAL_SERVER_ERROR):
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
        d = maybeDeferred(self.get_codec, request)
        d.addCallback(self.handle_request, request)
        d.addErrback(self.handle_request_error, request)
        return NOT_DONE_YET

    def handle_request(self, codec, request):
        d = self.decode_request(request, codec)
        d.addCallback(self.process_syncml, request)
        d.addCallback(self.encode_response, codec)
        d.addCallback(self.finish_request, request, codec.content_type)
        d.addErrback(self.handle_request_error, request)
        return NOT_DONE_YET

    def handle_request_error(self, failure, request):
        error = failure.value
        if not failure.check(TxSyncMLError):
            log.err(failure)
            error = TxSyncMLError(message='Internal server error.')

        request.setResponseCode(error.code)
        request.setHeader('Content-Type', 'text/plain')
        request.write(error.message)
        request.finish()

    def get_codec(self, request):
        codec = get_codec(request)
        if codec is None:
            raise ContentTypeError()
        return codec

    def decode_request(self, request, codec):
        content = request.content.read()

        def debug(xml):
            print minidom.parseString(xml).toprettyxml()
            return xml

        d = codec.decode(content)
        d.addCallback(debug)
        d.addCallback(SyncMLParser.parse)
        return d

    def encode_response(self, doc, codec):
        xml = doc.to_xml()
        print minidom.parseString(xml).toprettyxml()
        return codec.encode(xml)

    def finish_request(self, response, request, content_type):
        request.setHeader('Content-Type', content_type)
        request.write(response)
        request.finish()

    def authenticate_request(self, doc):
        header = doc.header
        [cred] = header.find('Cred')

        auth = AuthenticationBackend()
        return auth.authenticate(
            header.source.loc_uri, cred.type, cred.data)

    def process_syncml(self, doc, request):

        header = doc.header
        cred = header.find('Cred')
        if cred:
            d = self.authenticate_request(doc)
            d.addCallback(self.handle_authorized_syncml, doc)
            d.addErrback(self.handle_unauthorized_syncml, doc)
            return d
        return self.ask_for_authentication(doc, request)

    def handle_authorized_syncml(self, user, doc):

        request_body = doc.body
        request_header = doc.header
        device = user.current_device

        response_header = SyncHdr.create(
            request_header.session_id, request_header.msg_id,
            target=Target.create(request_header.source.loc_uri),
            source=Source.create(request_header.target.loc_uri))

        response_body = SyncBody.create()
        response_body.status(
            request_header.msg_id, request_header,
            constants.AUTHENTICATION_ACCEPTED,
            source_ref=request_header.source.loc_uri,
            target_ref=request_header.target.loc_uri)

        for put in request_body.puts:
            devinf = put.get_devinf()

            if devinf is not None:
                device.set_devinf(devinf)
                response_body.status(
                    request_header.msg_id, put, constants.STATUS_OK,
                    source_ref='./devinf11')
            else:
                request.request_devinf()

        for alert in request_body.alerts:
            print 'cmdid', alert.cmd_id
            print 'data', alert.data
            print 'locuri', alert.item.target.loc_uri

        return SyncML.create(header=response_header, body=response_body)

    def ask_for_authentication(self, doc, request):

        req_header = doc.header
        req_header.session_id
        req_header.msg_id

        header = SyncHdr.create(
            req_header.session_id, req_header.msg_id,
            target=Target.create(req_header.source.loc_uri),
            source=Source.create(req_header.target.loc_uri))
        body = SyncBody.create()
        print 'hello?!!!'
        body.status(
            req_header.msg_id, req_header, constants.AUTHORIZATION_REQUIRED,
            target_ref=req_header.target.loc_uri,
            source_ref=req_header.source.loc_uri,
            chal=Chal.create('nonce'))

        return SyncML.create(header=header, body=body)

    def handle_unauthorized_syncml(self, failure, doc):
        raise failure
