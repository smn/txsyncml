# -*- test-case-name: txsyncml.tests.test_commands -*-
import base64

from twisted.words.xish.domish import Element


class SyncMLElement(Element):

    def add(self, element):
        self.addChild(element)


class SyncML(SyncMLElement):

    def __init__(self, header=None, body=None):
        super(SyncML, self).__init__((None, 'SyncML'))
        if header is not None:
            self.add(header)
        if body is not None:
            self.add(body)


class SyncHdr(SyncMLElement):

    def __init__(self, session_id, msg_id,
                 target=None, source=None, cred=None, meta=None):
        super(SyncHdr, self).__init__((None, 'SyncHdr'))
        self.addElement('VerDTD', content='1.1')
        self.addElement('VerProto', content='SyncML/1.1')
        self.addElement('SessionID', content=unicode(session_id))
        self.addElement('MsgID', content=unicode(msg_id))

        if target is not None:
            self.add(target)

        if source is not None:
            self.add(source)

        if cred is not None:
            self.add(cred)

        if meta is not None:
            self.add(meta)


class Target(SyncMLElement):

    def __init__(self, loc_uri):
        super(Target, self).__init__((None, 'Target'))
        self.addElement('LocURI', content=unicode(loc_uri))


class Source(SyncMLElement):

    def __init__(self, loc_uri):
        super(Source, self).__init__((None, 'Source'))
        self.addElement('LocURI', content=unicode(loc_uri))


class Cred(SyncMLElement):

    def __init__(self, username, password, auth_type='syncml:auth-basic'):
        super(Cred, self).__init__((None, 'Cred'))

        self.add(Meta({
            'Type': auth_type,
        }))
        self.addElement('Data', content=base64.b64encode('%s:%s' % (
            username, password)))


class Meta(SyncMLElement):
    # NOTE: this needs some more thought, it's being too clever.
    def __init__(self, values={}):
        super(Meta, self).__init__((None, 'Meta'))
        for key, children in values.items():
            element = self.addElement(('syncml:metinf', key))
            if not isinstance(children, list):
                children = [children]

            for child in children:
                if isinstance(child, Element):
                    element.addChild(child)
                else:
                    element.addContent(unicode(child))


class SyncBody(SyncMLElement):

    def __init__(self, alert=None):
        super(SyncBody, self).__init__((None, 'SyncBody'))
        if alert is not None:
            self.add(alert)


class Alert(SyncMLElement):

    def __init__(self, cmd_id, code, items=[]):
        super(Alert, self).__init__((None, 'Alert'))
        self.addElement('CmdID', content=unicode(cmd_id))
        self.addElement('Data', content=unicode(code))
        for item in items:
            self.add(item)


class Item(SyncMLElement):

    def __init__(self, target, source, meta):
        super(Item, self).__init__((None, 'Item'))
        self.add(Target(target))
        self.add(Source(source))
        self.add(meta)


class Anchor(SyncMLElement):

    def __init__(self, last, next):
        super(Anchor, self).__init__(('syncml:metinf', 'Anchor'))
        self.addElement('Last', content=unicode(last))
        self.addElement('Next', content=unicode(next))
