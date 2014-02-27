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
        self.addElement('LocURI', content=loc_uri)


class Source(SyncMLElement):

    def __init__(self, loc_uri):
        super(Source, self).__init__((None, 'Source'))
        self.addElement('LocURI', content=loc_uri)


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
        for key, value in values.items():
            self.addElement(('syncml:metinf', key), content=value)
