# -*- coding: utf-8 -*-
from twisted.trial.unittest import TestCase
from twisted.internet.defer import inlineCallbacks

from txsyncml.codec import NoopCodec, WbXmlCodec


class NoopCodecTestCase(TestCase):

    def setUp(self):
        self.codec = NoopCodec()

    @inlineCallbacks
    def test_encode(self):
        byte_str = yield self.codec.encode('Zoe')
        self.assertEqual(byte_str, 'Zoe')

    @inlineCallbacks
    def test_decode(self):
        byte_str = yield self.codec.decode('Zoe')
        self.assertEqual(byte_str, 'Zoe')
