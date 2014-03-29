# -*- test-case-name: txsyncml.tests.test_resource -*-

from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred, Deferred
from twisted.python import log
from twisted.web.resource import Resource
from twisted.web import http
from twisted.web.server import NOT_DONE_YET

from txsyncml.codecs import get_codec
from txsyncml import constants
from txsyncml.commands import (
    SyncML, SyncHdr, SyncBody, Target, Source, Status, Chal)
from txsyncml.parser import SyncMLParser
from txsyncml.syncml import SyncMLEngine, UserState, AuthenticationBackend


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

        with open('request.wbxml', 'wb') as fp:
            fp.write(content)

        d = codec.decode(content)
        d.addCallback(SyncMLParser.parse)
        return d

    def encode_response(self, doc, codec):
        return codec.encode(doc.to_xml())

    def finish_request(self, response, request, content_type):
        request.setHeader('Content-Type', content_type)
        request.write(response)
        request.finish()

    def authenticate_request(self, doc):
        header = doc.header
        [cred] = header.find('Cred')

        auth = AuthenticationBackend()
        return auth.authenticate(cred.username, cred.password)

    def process_syncml(self, doc, request):

        header = doc.header
        cred = header.find('Cred')
        if cred:
            d = self.authenticate_request(doc)
            d.addCallback(self.handle_authorized_syncml, doc)
            d.addErrback(self.handle_unauthorized_syncml, doc)
            return d
        return self.ask_for_authentication(doc, request)

    def handle_authorized_syncml(self, user_state, doc):
        syncml_engine = SyncMLEngine(user_state)
        syncml_engine.process(doc)

        header = SyncHdr.create(
            1, 1,
            target=Target.create('target'),
            source=Source.create('source'))
        body = SyncBody.create(
            statuses=[
                Status.create(cmd_id=1, msg_ref=1, cmd_ref=0, cmd='SyncHdr',
                              target_ref='http://www.syncml.org/sync-server',
                              source_ref='IMEI:493005100592800',
                              code=constants.AUTHENTICATION_ACCEPTED)])
        return SyncML.create(header=header, body=body)

    def ask_for_authentication(self, doc, request):

        req_header = doc.header
        req_header.session_id
        req_header.msg_id

        header = SyncHdr.create(
            req_header.session_id, req_header.msg_id,
            target=Target.create(req_header.source.loc_uri),
            source=Source.create(req_header.target.loc_uri))
        body = SyncBody.create(
            statuses=[
                Status.create(cmd_id=1, msg_ref=req_header.msg_id,
                              cmd_ref=0, cmd='SyncHdr',
                              target_ref=req_header.target.loc_uri,
                              source_ref=req_header.source.loc_uri,
                              code=constants.AUTHORIZATION_REQUIRED,
                              chal=Chal.create('nonce'))])
        return SyncML.create(header=header, body=body)

    def handle_unauthorized_syncml(self, failure):
        raise NotImplementedError('Not implemented yet')
