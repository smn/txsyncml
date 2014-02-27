# -*- test-case-name: txsyncml.tests.test_wbxml -*-

import os

from twisted.internet.defer import Deferred
from twisted.internet import protocol
from twisted.internet import reactor


class WbXmlProcessProtocol(protocol.ProcessProtocol):

    def __init__(self, data, deferred):
        self.data = data
        self.deferred = deferred

    def connectionMade(self):
        self.transport.write(self.data)
        self.transport.closeStdin()

    def outReceived(self, data):
        self.deferred.callback(data)
        self.transport.loseConnection()


def xml2wbxml(xml, version='1.2'):
    d = Deferred()
    protocol = WbXmlProcessProtocol(xml, d)
    reactor.spawnProcess(
        protocol, '/usr/local/bin/xml2wbxml',
        ['xml2wbxml', '-o', '-', '-v', version, '-'],
        env={'HOME': os.environ['HOME']})
    return d


def wbxml2xml(wbxml, language_type='SYNCML11', charset='UTF-8'):
    d = Deferred()
    protocol = WbXmlProcessProtocol(wbxml, d)
    reactor.spawnProcess(
        protocol, '/usr/local/bin/wbxml2xml',
        ['wbxml2xml', '-o', '-', '-l', language_type, '-c', charset, '-'],
        env={'HOME': os.environ['HOME']})
    return d
