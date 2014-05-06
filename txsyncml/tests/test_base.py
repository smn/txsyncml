import os
from xml.etree.ElementTree import XML

from twisted.trial.unittest import TestCase


class TxSyncMLTestCase(TestCase):

    timeout = int(os.environ.get('TXSYNCML_TEST_TIMEOUT', 1))

    def assertXPath(self, xpath, xml, count=1):
        doc = XML(xml)
        matches = doc.findall(xpath)
        self.assertEqual(len(matches), count, '%s does not have %s of %r.' % (
            xml, count, xpath))
        return matches
