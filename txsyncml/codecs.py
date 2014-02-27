# -*- test-case-name: txsyncml.tests.test_codecs -*-
from twisted.internet.defer import succeed

from txsyncml.wbxml import xml2wbxml, wbxml2xml


class NoopCodec(object):

    content_type = 'application/vnd.syncml+xml'

    def encode(self, data):
        return succeed(data)

    def decode(self, data):
        return succeed(data)


class WbXmlCodec(NoopCodec):

    content_type = 'application/vnd.syncml+wbxml'

    def encode(self, data):
        return xml2wbxml(data)

    def decode(self, data):
        return wbxml2xml(data)


codecs = [
    NoopCodec(),
    WbXmlCodec(),
]


def get_codec(request):
    # NOTE: I'm ignoring content-type in the format
    #       'application/json; charset=utf-8'. Burn that bridge when
    #       I get there.
    [content_type] = request.requestHeaders.getRawHeaders('Content-Type')
    for codec in codecs:
        if codec.content_type == content_type:
            return codec
