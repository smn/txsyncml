import os.path
import pkg_resources

from twisted.internet import reactor
from twisted.internet.task import Clock
from twisted.trial.unittest import TestCase
from twisted.web.client import HTTPConnectionPool
from twisted.web import server

from treq.client import HTTPClient

from txsyncml.resource import TxSyncMLResource


class TxSyncMLResourceTestCase(TestCase):

    def setUp(self):
        self.clock = Clock()
        self.pool = HTTPConnectionPool(self.clock, persistent=False)
        self.client = HTTPClient.with_config(
            pool=self.pool, allow_redirects=False, reactor=self.clock)
        self.resource = TxSyncMLResource(self.clock)
        self.site = server.Site(self.resource)
        self.listener = reactor.listenTCP(0, self.site, interface='localhost')
        self.listener_port = self.listener.getHost().port
        self.addCleanup(self.listener.loseConnection)
        self.addCleanup(self.pool.closeCachedConnections)

    def get_fixture(self, fixture_name):
        path = pkg_resources.resource_filename('txsyncml.tests.fixtures',
                                               fixture_name)
        with open(path, 'r') as fp:
            data = fp.read()
        return data

    def make_url(self, *paths):
        return 'http://localhost:%s/%s' % (
            self.listener_port, ('/'.join(map(str, paths)) + '/'
                                 if paths else ''))

    def send_syncml(self, fixture_name):
        self.client.post(self.make_url(), data=)

    def test_client_sync_init(self):
        print self.make_url('foo')
