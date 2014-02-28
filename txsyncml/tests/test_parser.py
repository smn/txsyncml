from twisted.trial.unittest import TestCase

from txsyncml.parser import SyncMLParser
from txsyncml.tests.helpers import FixtureHelper


class SyncMLParserTestCase(TestCase):

    def setUp(self):
        self.parser = SyncMLParser()
        self.fixtures = FixtureHelper()

    def test_parsing(self):
        data = self.fixtures.get_fixture('client_sync_init.xml')
        result = self.parser.parse(data)
        result.dump()
