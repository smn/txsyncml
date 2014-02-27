# -*- test-case-name: txsyncml.tests.test_parser -*-

from twisted.python import log
from twisted.web.sux import XMLParser
from twisted.words.xish.domish import Element


class SyncMLParser(XMLParser):

    def __init__(self):
        self.connectionMade()
        self.chain = []
        self.registry = []

    def parse(self, data):
        self.dataReceived(data)

    def gotTagStart(self, tagname, attrs):

        element = Element((None, tagname))
        for key, value in attrs.items():
            element[key] = value

        self.chain.append(element)

    def gotText(self, text):
        self.current_text = text

    def gotTagEnd(self, tagname):
        handler = getattr(self, 'on_%s' % (tagname.lower(),),
                          self.ignored_tag)
        element = self.chain.pop()
        if self.current_text:
            element.addContent(self.current_text)

        if self.chain:
            parent = self.chain[-1]
            parent.addChild(element)

        handler(element)

    def ignored_tag(self, element):
        log.msg('Ignoring %s' % (element.name,))
