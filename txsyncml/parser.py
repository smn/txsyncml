# -*- test-case-name: txsyncml.tests.test_parser -*-

from twisted.web.sux import XMLParser

from txsyncml import commands


class SyncMLParser(XMLParser):

    def __init__(self):
        self.connectionMade()
        self.chain = []
        self.registry = []
        self.root = None

    def parse(self, data):
        self.dataReceived(data)
        return self.root

    def gotTagStart(self, tagname, attrs):
        klass = getattr(commands, tagname)
        self.chain.append(klass(tagname, None))

    def gotText(self, text):
        self.chain[-1].value = text

    def gotTagEnd(self, tagname):
        element = self.chain.pop()
        if self.chain:
            parent = self.chain[-1]
            parent.add_child(element)
        else:
            self.root = element
