from base64 import b64encode

from twisted.trial.unittest import TestCase
from twisted.words.xish.domish import Element

from txsyncml.commands import (
    SyncML, SyncHdr, Target, Source, Cred, Meta, SyncBody, Item, Alert,
    Anchor)


class SyncMLElementTestCase(TestCase):

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
        el = Element((None, 'one'))
        el.addContent('ok')
        self.assertXml(
            Meta({
                'Foo': ['Bar'],
                'Baz': [el]}),
            "<Meta>"
            "<Foo xmlns='syncml:metinf'>Bar</Foo>"
            "<Baz xmlns='syncml:metinf'>"
            "<one>ok</one>"
            "</Baz>"
            "</Meta>")

    def test_syncbody(self):
        self.assertXml(
            SyncBody(),
            '<SyncBody/>')

    def test_item(self):
        meta = Meta()
        meta.add(Anchor(234, 276))
        item = Item('target', 'source', meta)
        self.assertXml(
            item,
            "<Item>"
            "<Target>"
            "<LocURI>target</LocURI>"
            "</Target>"
            "<Source>"
            "<LocURI>source</LocURI>"
            "</Source>"
            "<Meta>"
            "<Anchor xmlns='syncml:metinf'>"
            "<Last>234</Last>"
            "<Next>276</Next>"
            "</Anchor>"
            "</Meta>"
            "</Item>")

    def test_alert(self):
        self.assertXml(
            Alert(1, 203, []),
            "<Alert>"
            "<CmdID>1</CmdID>"
            "<Data>203</Data>"
            "</Alert>")

    def test_anchor(self):
        self.assertXml(
            Anchor('last', 'next'),
            "<Anchor xmlns='syncml:metinf'>"
            "<Last>last</Last>"
            "<Next>next</Next>"
            "</Anchor>")
