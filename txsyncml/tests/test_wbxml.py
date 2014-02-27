from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase
from twisted.web import microdom

from txsyncml.codecs import WbXmlCodec
from txsyncml.commands import (
    SyncML, SyncHdr, Target, Source, Cred, Meta, SyncBody, Item, Alert,
    Anchor)
from txsyncml.wbxml import wbxml2xml, xml2wbxml
from txsyncml.tests.helpers import FixtureHelper, SyncMLClientHelper


class WbXmlTestCase(TestCase):

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

    @inlineCallbacks
    def test_build_client_sync_init(self):
        codec = WbXmlCodec()
        syncml = self.client.build_request()
        wbxml = yield codec.encode(syncml.toXml())
        expected_wbxml = self.fixtures.get_fixture('client_sync_init.wbxml')
        self.assertEqual(wbxml, expected_wbxml)
