from base64 import b64encode

from twisted.trial.unittest import TestCase

from txsyncml.commands import SyncML, SyncHdr, Target, Source, Cred, Meta


class SyncMLElementTestCase(TestCase):

    def setUp(self):
        pass

    def assertXml(self, element, xml_str):
        self.assertEqual(element.toXml(), xml_str)

    def test_syncml(self):
        self.assertXml(SyncML(), '<SyncML/>')

    def test_synchdr(self):
        self.assertXml(
            SyncHdr('1', '1'),
            '<SyncHdr>'
            '<VerDTD>1.1</VerDTD>'
            '<VerProto>SyncML/1.1</VerProto>'
            '<SessionID>1</SessionID>'
            '<MsgID>1</MsgID>'
            '</SyncHdr>')

    def test_target(self):
        self.assertXml(
            Target('foo'),
            '<Target>'
            '<LocURI>foo</LocURI>'
            '</Target>')

    def test_source(self):
        self.assertXml(
            Source('foo'),
            '<Source>'
            '<LocURI>foo</LocURI>'
            '</Source>')

    def test_cred(self):
        self.assertXml(
            Cred('foo', 'bar', auth_type='some-algorithm'),
            "<Cred>"
            "<Meta>"
            "<Type xmlns='syncml:metinf'>some-algorithm</Type>"
            "</Meta>"
            "<Data>%s</Data>"
            "</Cred>" % (b64encode("foo:bar")))

    def test_meta(self):
        self.assertXml(
            Meta({'Foo': 'Bar'}),
            "<Meta>"
            "<Foo xmlns='syncml:metinf'>Bar</Foo>"
            "</Meta>")
