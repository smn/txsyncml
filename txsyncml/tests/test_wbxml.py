from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase
from twisted.web import microdom

from txsyncml.codecs import WbXmlCodec
from txsyncml.commands import (
    SyncML, SyncHdr, Target, Source, Cred, Meta, SyncBody, Item, Alert,
    Anchor)
from txsyncml.wbxml import wbxml2xml, xml2wbxml
from txsyncml.tests.helpers import FixtureHelper


class WbXmlTestCase(TestCase):

    def setUp(self):
        self.fixtures = FixtureHelper()

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
        header = SyncHdr(
            1, 1,
            target=Target('http://www.syncml.org/sync-server'),
            source=Source('IMEI:493005100592800'),
            cred=Cred('Bruce2', 'OhBehave'),  # Sample from the spec
            meta=Meta({
                'MaxMsgSize': 5000
            }))
        meta = Meta()
        meta.add(Anchor(234, 276))
        item = Item('./contacts/james_bond', './dev-contacts', meta)
        alert = Alert(1, 200, items=[item])
        body = SyncBody(alert=alert)

        syncml = SyncML(header=header, body=body)
        codec = WbXmlCodec()
        wbxml = yield codec.encode(syncml.toXml())
        expected_wbxml = self.fixtures.get_fixture('client_sync_init.wbxml')
        self.assertEqual(wbxml, expected_wbxml)
