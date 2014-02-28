# -*- test-case-name: txsyncml.tests.test_commands -*-
import base64

from twisted.words.xish.domish import Element


class SyncMLElement(object):

    def __init__(self, name, value, ns=None):
        self.name = name
        self.value = value
        self.ns = ns

    def build(self):
        element = Element((self.ns, self.name))
        if isinstance(self.value, list):
            for item in self.value:
                element.addChild(item.build())
        else:
            element.addContent(self.value)
        return element


class SyncML(SyncMLElement):

    def __init__(self, header=None, body=None):
        self.header = header
        self.body = body

    def build(self):
        element = Element((None, 'SyncML'))
        if self.header is not None:
            element.addChild(self.header.build())
        if self.body is not None:
            element.addChild(self.body.build())
        return element


class SyncHdr(SyncMLElement):

    def __init__(self, session_id, msg_id,
                 target=None, source=None, cred=None, meta=None):
        self.session_id = session_id
        self.msg_id = msg_id
        self.target = target
        self.source = source
        self.cred = cred
        self.meta = meta

    def build(self):
        element = Element((None, 'SyncHdr'))
        element.addElement('VerDTD', content='1.1')
        element.addElement('VerProto', content='SyncML/1.1')
        element.addElement('SessionID', content=unicode(self.session_id))
        element.addElement('MsgID', content=unicode(self.msg_id))

        if self.target is not None:
            element.addChild(self.target.build())

        if self.source is not None:
            element.addChild(self.source.build())

        if self.cred is not None:
            element.addChild(self.cred.build())

        if self.meta is not None:
            element.addChild(self.meta.build())
        return element


class Target(SyncMLElement):

    def __init__(self, loc_uri):
        self.loc_uri = loc_uri

    def build(self):
        element = Element((None, 'Target'))
        element.addElement('LocURI', content=unicode(self.loc_uri))
        return element


class Source(SyncMLElement):

    def __init__(self, loc_uri):
        self.loc_uri = loc_uri

    def build(self):
        element = Element((None, 'Source'))
        element.addElement('LocURI', content=unicode(self.loc_uri))
        return element


class Data(SyncMLElement):
    def __init__(self, content):
        self.content = content

    def build(self):
        element = Element((None, 'Data'))
        element.addContent(unicode(self.content))
        return element


class Cred(SyncMLElement):

    def __init__(self, username, password, auth_type='syncml:auth-basic'):
        self.username = username
        self.password = password
        self.auth_type = auth_type

    def build(self):
        element = Element((None, 'Cred'))
        element.addChild(
            Meta([
                SyncMLElement('Type', self.auth_type, 'syncml:metinf')
            ]).build())
        element.addChild(
            Data(base64.b64encode('%s:%s' % (
                self.username, self.password))).build())
        return element


class Meta(SyncMLElement):
    def __init__(self, children=[]):
        self.children = children

    def build(self):
        element = Element((None, 'Meta'))
        for child in self.children:
            element.addChild(child.build())
        return element


class SyncBody(SyncMLElement):

    def __init__(self, alerts=[], statuses=[]):
        self.alerts = alerts
        self.statuses = statuses

    def build(self):
        element = Element((None, 'SyncBody'))
        for alert in self.alerts:
            element.addChild(alert.build())

        for status in self.statuses:
            element.addChild(status.build())
        return element


class Alert(SyncMLElement):

    def __init__(self, cmd_id, code, items=[]):
        self.cmd_id = cmd_id
        self.code = code
        self.items = items

    def build(self):
        element = Element((None, 'Alert'))
        element.addElement('CmdID', content=unicode(self.cmd_id))
        element.addElement('Data', content=unicode(self.code))
        for item in self.items:
            element.addChild(item.build())
        return element


class Item(SyncMLElement):

    def __init__(self, target, source, meta):
        self.target = target
        self.source = source
        self.meta = meta

    def build(self):
        element = Element((None, 'Item'))
        element.addChild(Target(self.target).build())
        element.addChild(Source(self.source).build())
        element.addChild(self.meta.build())
        return element


class Anchor(SyncMLElement):

    def __init__(self, last, next):
        self.last = last
        self.next = next

    def build(self):
        element = Element(('syncml:metinf', 'Anchor'))
        element.addElement('Last', content=unicode(self.last))
        element.addElement('Next', content=unicode(self.next))
        return element


class Status(SyncMLElement):

    def __init__(self, cmd_id, msg_ref, cmd_ref, cmd,
                 target_ref, source_ref, code):
        self.cmd_id = cmd_id
        self.msg_ref = msg_ref
        self.cmd_ref = cmd_ref
        self.cmd = cmd
        self.target_ref = target_ref
        self.source_ref = source_ref
        self.code = code

    def build(self):
        element = Element((None, 'Status'))
        element.addElement('CmdID', content=unicode(self.cmd_id))
        element.addElement('MsgRef', content=unicode(self.msg_ref))
        element.addElement('CmdRef', content=unicode(self.cmd_ref))
        element.addElement('Cmd', content=self.cmd)
        element.addElement('TargetRef', content=self.target_ref)
        element.addElement('SourceRef', content=self.source_ref)
        element.addChild(Data(self.code).build())
        return element
