# -*- test-case-name: txsyncml.tests.test_parser -*-

from twisted.web.sux import XMLParser

from txsyncml.commands import SyncMLElement


class ParsedElement(object):

    def __init__(self, name, value=None, attrs={}, children=None):
        self.name = name
        self.value = value
        self.attrs = {}
        self.children = ([] if children is None else children)

    def append(self, child):
        self.children.append(child)

    def __repr__(self):
        return '<ParsedElement name=%r, value=%r, attrs=%r children=%r>' % (
            self.name, self.value, self.attrs, self.children)

    def dump(self, indentation=0):
        """
        Debug method to see what's going on
        """
        def i(s):
            print (indentation * '  ') + s
        i('Name: %r' % (self.name,))
        i('Value: %r' % (self.value,))
        i('Attrs: %r' % (self.attrs,))
        i('Children:')
        for child in self.children:
            child.dump(indentation=indentation+1)


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
        pe = ParsedElement(tagname, attrs=attrs)
        self.chain.append(pe)

    def gotText(self, text):
        self.chain[-1].value = text

    def gotTagEnd(self, tagname):
        pe = self.chain.pop()

        handler_func_name = 'on_%s' % (pe.name.lower())
        handler = getattr(self, handler_func_name, self.noop)
        parsed = handler(pe)

        if self.chain:
            parent = self.chain[-1]
            parent.append(parsed)
        else:
            self.root = parsed

    def noop(self, element):
        return element
