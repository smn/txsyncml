# -*- test-case-name: txsyncml.tests.test_parser -*-

from twisted.web.sux import XMLParser

from txsyncml import commands


class SyncMLParserException(Exception):
    pass


class SyncMLParser(XMLParser):

    def __init__(self):
        self.chain = []
        self.registry = []
        self.root = None

    @classmethod
    def parse(cls, data):
        parser = cls()
        parser.connectionMade()
        parser.dataReceived(data)
        return parser.root

    def gotTagStart(self, tagname, attrs):
        # some class names have hyphens
        tagname = tagname.replace('-', '_')
        try:
            klass = getattr(commands, tagname)
        except AttributeError:
            klass = commands.oneof(tagname)
        self.chain.append(klass(tagname, None))

    def gotText(self, text):
        # This happens when a DTD is parsed
        if self.chain:
            self.chain[-1].value = text

    def gotDoctype(self, doctype):
        pass

    def gotTagEnd(self, tagname):
        element = self.chain.pop()
        if self.chain:
            parent = self.chain[-1]
            try:
                parent.add_child(element)
            except commands.SyncMLError:
                print 'forcing', element.__class__, 'under', parent.__class__
                parent.allowed_children.append(element.__class__)
                parent.add_child(element)
        else:
            self.root = element
