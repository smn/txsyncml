# -*- test-case-name: txsyncml.tests.test_parser -*-

from twisted.internet.defer import Deferred
from twisted.web.sux import XMLParser
from twisted.words.xish.domish import Element


class BaseParser(XMLParser):

    def __init__(self):
        self.connectionMade()
        self.chain = []
        self.registry = []

    def gotTagStart(self, tagname, attrs):
        element = Element((None, tagname))
        for key, value in attrs.items():
            element[key] = value
        self.chain.append(element)

    def gotText(self, text):
        self.current_text = text

    def gotTagEnd(self, tagname):
        element = self.chain.pop()
        if self.current_text:
            element.addContent(self.current_text)

        if self.chain:
            self.parent = self.chain[-1]
            self.parent.addChild(element)
            handler_func_name = 'on_%s_in_%s' % (element.name.lower(),
                                                 self.parent.name.lower())
        else:
            self.parent = None
            handler_func_name = 'on_%s' % (element.name.lower())

        handler = getattr(self, handler_func_name, self.noop)
        handler(element)

    def noop(self, element):
        pass


class SyncMLParser(BaseParser):

    def __init__(self):
        BaseParser.__init__(self)
        self.syncml_state = None

    def parse(self, data):
        self.dataReceived(data)

    def on_synchdr_in_syncml(self, synchdr):
        self.switch_state('HEADER')

    def on_syncbody_in_syncml(self, syncbody):
        self.switch_state('BODY')

    def on_alert_in_syncbody(self, alert):
        print 'parent', self.parent.name
        print 'hi!', alert.name

    def on_verdtd_in_synchdr(self, verdtd):
        print 'got', verdtd.name

    def switch_state(self, state):
        self.syncml_state = state
        print 'state:', state
