from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase
from twisted.web.client import HTTPConnectionPool
from twisted.web import http
from twisted.web import server

from treq import content
from treq.client import HTTPClient

from txsyncml.resource import TxSyncMLResource
from txsyncml.tests.helpers import FixtureHelper
from txsyncml.codecs import NoopCodec, WbXmlCodec


class TxSyncMLResourceTestCase(TestCase):

    timeout = 1
    content_type = 'application/vnd.syncml+xml'
    codec = NoopCodec

    def setUp(self):
        self.pool = HTTPConnectionPool(reactor, persistent=False)
        self.client = HTTPClient.with_config(
            pool=self.pool, allow_redirects=False, reactor=reactor)
        self.resource = TxSyncMLResource(reactor)
        self.site = server.Site(self.resource)
        self.listener = reactor.listenTCP(0, self.site, interface='localhost')
        self.listener_port = self.listener.getHost().port
        self.fixtures = FixtureHelper()
        self.addCleanup(self.listener.loseConnection)
        self.addCleanup(self.pool.closeCachedConnections)

    def make_url(self, *paths):
        return 'http://localhost:%s/%s' % (
            self.listener_port, ('/'.join(map(str, paths)) + '/'
                                 if paths else ''))

    def request(self, fixture_name, headers={}):
        default_headers = {
            'Content-Type': [self.content_type],
        }
        default_headers.update(headers)
        data = self.fixtures.get_fixture(fixture_name)
        d = self.encode_request_data(data)
        d.addCallback(
            lambda data: self.client.post(self.make_url(), data=data,
                                          headers=default_headers))
        return d

    def encode_request_data(self, data):
        return self.codec().encode(data)

    def assertContentType(self, request, content_type):
        headers = request.headers
        [found_content_type] = headers.getRawHeaders('Content-Type')
        self.assertEqual(
            content_type, found_content_type,
            "Content-Types %r and %r don't match." % (
                content_type, found_content_type))

    @inlineCallbacks
    def test_invalid_content_type(self):
        response = yield self.request('client_sync_init.xml', {
            'Content-Type': ['foo'],
        })
        body = yield content(response)
        self.assertEqual(response.code, http.NOT_ACCEPTABLE)
        self.assertContentType(response, 'text/plain')
        self.assertEqual(body, 'Unsupported content-type.')

    @inlineCallbacks
    def test_client_sync_init(self):
        response = yield self.request('client_sync_init.xml')
        self.assertContentType(response, self.content_type)
        print dict(response.headers.getAllRawHeaders())
        # print (yield content(response))


class TxSyncMLResourceWapBinaryXmlTestCase(TxSyncMLResourceTestCase):

    content_type = 'application/vnd.syncml+wbxml'
    codec = WbXmlCodec
