from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.trial.unittest import TestCase
from twisted.web.client import HTTPConnectionPool
from twisted.web import http
from twisted.web import server

from treq import content
from treq.client import HTTPClient

from txsyncml.resource import TxSyncMLResource
from txsyncml.tests.helpers import FixtureHelper
from txsyncml.wbxml import xml2wbxml


class TxSyncMLResourceTestCase(TestCase):

    timeout = 1
    encode_wbxml = False

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

    @inlineCallbacks
    def send_syncml(self, fixture_name, headers=None):
        if self.encode_wbxml:
            default_headers = {
                'Content-Type': ['application/vnd.syncml+wbxml'],
            }
            data = yield xml2wbxml(self.fixtures.get_fixture(fixture_name))
        else:
            default_headers = {
                'Content-Type': ['application/vnd.syncml+xml'],
            }
            data = self.fixtures.get_fixture(fixture_name)

        if headers is not None:
            default_headers.update(headers)

        response = yield self.client.post(self.make_url(), data=data,
                                          headers=default_headers)
        returnValue(response)

    @inlineCallbacks
    def test_invalid_content_type(self):
        response = yield self.send_syncml('client_sync_init.xml', {
            'Content-Type': ['foo'],
        })
        body = yield content(response)
        self.assertEqual(response.code, http.NOT_ACCEPTABLE)
        self.assertEqual(body, 'Unsupported content-type.')

    @inlineCallbacks
    def test_client_sync_init(self):
        response = yield self.send_syncml('client_sync_init.xml')
        # print dict(response.headers.getAllRawHeaders())
        # print (yield content(response))


class TxSyncMLResourceWapBinaryXmlTestCase(TxSyncMLResourceTestCase):

    timeout = 1
    encode_wbxml = True
