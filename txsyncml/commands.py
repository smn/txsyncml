# -*- test-case-name: txsyncml.tests.test_commands -*-
import base64

from twisted.words.xish.domish import Element


class SyncMLElement(Element):

    def add(self, element):
        self.addChild(element)


class SyncML(SyncMLElement):

    def __init__(self):
        super(SyncML, self).__init__((None, 'SyncML'))


class SyncHdr(SyncMLElement):

    def __init__(self, session_id, msg_id):
        super(SyncHdr, self).__init__((None, 'SyncHdr'))
        self.addElement('VerDTD', content='1.1')
        self.addElement('VerProto', content='SyncML/1.1')
        self.addElement('SessionID', content=session_id)
        self.addElement('MsgID', content=msg_id)


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

    def __init__(self, values):
        super(Meta, self).__init__((None, 'Meta'))
        for key, children in values.items():
            element = self.addElement(('syncml:metinf', key))
            for child in children:
                if isinstance(child, Element):
                    element.addChild(child)
                else:
                    element.addContent(child)


class SyncBody(SyncMLElement):

    def __init__(self):
        super(SyncBody, self).__init__((None, 'SyncBody'))


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
