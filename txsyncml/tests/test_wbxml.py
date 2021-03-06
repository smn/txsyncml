from twisted.internet.defer import inlineCallbacks
from twisted.web import microdom

from txsyncml.wbxml import wbxml2xml, xml2wbxml
from txsyncml.tests.helpers import FixtureHelper, SyncMLClientHelper
from txsyncml.tests.test_base import TxSyncMLTestCase


class WbXmlTestCase(TxSyncMLTestCase):

    def setUp(self):
        self.fixtures = FixtureHelper()
        self.client = SyncMLClientHelper()

    @inlineCallbacks
    def test_encode_decode(self):
        # FIXME: this test is rather weak
        fixture_xml = self.fixtures.get_fixture('client_sync_init.xml')
        wbxml = yield xml2wbxml(fixture_xml)
        xml = yield wbxml2xml(wbxml)
        dom = microdom.parseXMLString(xml)
        [ver_proto] = dom.getElementsByTagName('VerProto')
        self.assertEqual(ver_proto.firstChild().value, 'SyncML/1.1')
