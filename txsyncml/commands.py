# -*- test-case-name: txsyncml.tests.test_commands -*-
from base64 import b64encode
from hashlib import md5

from twisted.words.xish.domish import Element


class SyncMLError(Exception):
    pass


class SyncMLElement(object):

    allowed_children = []

    def __init__(self, name, value, ns=None, children=[]):
        self.name = name
        self.value = value
        self.ns = ns
        self.children = []
        for child in children:
            self.add_child(child)

    def add_child(self, child):
        if child.__class__ not in self.allowed_children:
            raise SyncMLError('Child %r not allowed for %r.' % (
                child.__class__, self.__class__))
        self.children.append(child)

    def build(self):
        element = self.build_children(self.build_root())
        if self.value is not None:
            element.addContent(self.value)
        return element

    def build_root(self):
        return Element((self.ns, self.name))

    def build_children(self, element):
        for allowed_child in self.allowed_children:
            for child in self.find(allowed_child):
                element.addChild(child.build())
        return element

    def to_xml(self):
        return self.build().toXml()

    def find(self, child_name):
        if not isinstance(child_name, basestring):
            child_name = child_name.__name__
        return [child for child in self.children if child.name == child_name]


class SessionID(SyncMLElement):

    @classmethod
    def create(cls, session_id):
        return cls('SessionID', unicode(session_id))


class MsgID(SyncMLElement):

    @classmethod
    def create(cls, msg_id):
        return cls('MsgID', unicode(msg_id))


class LocURI(SyncMLElement):

    @classmethod
    def create(cls, loc_uri):
        return cls('LocURI', unicode(loc_uri))


class LocName(SyncMLElement):

    @classmethod
    def create(cls, loc_name):
        return cls('LocName', unicode(loc_name))


class Target(SyncMLElement):

    allowed_children = [LocURI]

    @classmethod
    def create(cls, loc_uri):
        return cls('Target', None, children=[LocURI.create(loc_uri)])

    @property
    def loc_uri(self):
        [loc_uri] = self.find('LocURI')
        return loc_uri.value


class Source(SyncMLElement):

    allowed_children = [LocURI, LocName]

    @classmethod
    def create(cls, loc_uri):
        return cls('Source', None, children=[LocURI.create(loc_uri)])

    @property
    def loc_uri(self):
        [loc_uri] = self.find('LocURI')
        return loc_uri.value


class Type(SyncMLElement):

    @classmethod
    def create(cls, auth_type):
        return cls('Type', auth_type, ns='syncml:metinf')


class Next(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('Next', unicode(value))


class Last(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('Last', unicode(value))


class Anchor(SyncMLElement):

    allowed_children = [Last, Next]

    @classmethod
    def create(cls, last, next):
        return cls('Anchor', None, ns='syncml:metinf', children=[
            Last.create(last),
            Next.create(next),
        ])


class MaxMsgSize(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('MaxMsgSize', unicode(value), ns='syncml:metinf')


class VerDTD(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('VerDTD', unicode(value))


class TargetRef(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('TargetRef', unicode(value))


class SourceRef(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('SourceRef', unicode(value))


def oneof(name, allowed_children=[]):
    return type(name, (SyncMLElement,), {
        'allowed_children': allowed_children
    })

Man = oneof('Man')
Mod = oneof('Mod')
FwV = oneof('FwV')
SwV = oneof('SwV')
HwV = oneof('HwV')
DevID = oneof('DevID')
DevTyp = oneof('DevTyp')
UTC = oneof('UTC')
DisplayName = oneof('DisplayName')
MaxGUIDSize = oneof('MaxGUIDSize')
CTType = oneof('CTType')
VerCT = oneof('VerCT')
Rx_Pref = oneof('Rx-Pref', [
    CTType,
    VerCT
])
Tx_Pref = oneof('Tx-Pref', [
    CTType,
    VerCT
])
Rx = oneof('Rx', [
    CTType,
    VerCT
])
Tx = oneof('Tx', [
    CTType,
    VerCT
])
PropName = oneof('PropName')
MaxSize = oneof('MaxSize')
ParamName = oneof('ParamName')
ValEnum = oneof('ValEnum')
MaxOccur = oneof('MaxOccur')
NoTruncate = oneof('NoTruncate')
PropParam = oneof('PropParam', [
    ParamName,
    ValEnum,
])
MaxID = oneof('MaxID')
DSMem = oneof('DSMem', [
    MaxID,
])
Property = oneof('Property', [
    PropName,
    MaxSize,
    MaxOccur,
    NoTruncate,
    PropParam,
    ValEnum
])
Size = oneof('Size')
CTCap = oneof('CTCap', [
    CTType,
    VerCT,
    Property,
    PropName,
    Size,
    ParamName,
    ValEnum,
])

SupportLargeObjs = oneof('SupportLargeObjs')
SyncType = oneof('SyncType')
SyncCap = oneof('SyncCap', [
    SyncType
])

DataStore = oneof('DataStore', [
    SourceRef,
    DisplayName,
    MaxGUIDSize,
    Rx_Pref,
    Rx,
    Tx_Pref,
    Tx,
    CTCap,
    DSMem,
    SyncCap,
])

MaxObjSize = oneof('MaxObjSize')

FreeMem = oneof('FreeMem')
FreeID = oneof('FreeID')

Mem = oneof('Mem', [
    FreeMem,
    FreeID,
])

Final = oneof('Final')


class Format(SyncMLElement):

    @classmethod
    def create(cls, format_type):
        return cls('Format', format_type, ns='syncml:metinf')


class NextNonce(SyncMLElement):

    @classmethod
    def create(cls, nonce):
        return cls('NextNonce', nonce.encode('base64'), ns='syncml:metinf')


class Meta(SyncMLElement):

    allowed_children = [Type, Anchor, MaxMsgSize, MaxObjSize, Mem, Format,
                        NextNonce]

    @classmethod
    def create(cls, children=[]):
        return cls('Meta', None, children=children)


class DevInf(SyncMLElement):

    allowed_children = [
        VerDTD,
        Man,
        Mod,
        FwV,
        SwV,
        HwV,
        DevID,
        DevTyp,
        UTC,
        SupportLargeObjs,
        DataStore,
        CTCap,
    ]


class Data(SyncMLElement):

    allowed_children = [
        DevInf,
    ]

    @classmethod
    def create(cls, content):
        return cls('Data', unicode(content))


def md5digest(m):
    return md5(m).digest()


def md5_cred_hasher(username, password, nonce):
    return b64encode(
        md5digest(
            '%s:%s' % (
                b64encode(
                    md5digest('%s:%s' % (username, password))
                ), nonce))
    ).strip()


def base64_cred_hasher(username, password, nonce=None):
    # NOTE: Nonce is not used for base64 hashes
    return ('%s:%s' % (username, password)).encode('base64').strip()


class Cred(SyncMLElement):

    allowed_children = [Meta, Data]
    auth_type_encoders = {
        'syncml:auth-basic': base64_cred_hasher,
        'syncml:auth-md5': md5_cred_hasher,
    }

    @classmethod
    def create(cls, username, password, nonce=None,
               auth_type='syncml:auth-basic', format='b64'):
        if auth_type not in cls.auth_type_encoders:
            raise SyncMLError('Unsupported Cred auth type: %r' % (
                auth_type,))
        encoder = cls.auth_type_encoders[auth_type]
        return cls('Cred', None, children=[
            Meta.create([
                Type.create(auth_type),
                Format.create(format)]),
            Data.create(encoder(username, password, nonce))
        ])

    @property
    def type(self):
        [meta] = self.find('Meta')
        [type_] = meta.find('Type')
        return type_.value

    @property
    def data(self):
        [data] = self.find('Data')
        return data.value


class VerProto(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('VerProto', unicode(value))


class SyncHdr(SyncMLElement):

    allowed_children = [
        VerDTD,
        VerProto,
        SessionID,
        MsgID,
        Target,
        Source,
        Cred,
        Meta,
    ]

    @classmethod
    def create(cls, session_id, msg_id,
               target=None, source=None, cred=None, meta=None, ver_dtd='1.1',
               ver_proto='SyncML/1.1'):

        children = [
            VerDTD.create(ver_dtd),
            VerProto.create(ver_proto),
            SessionID.create(session_id),
            MsgID.create(msg_id)
        ]

        if target is not None:
            children.append(target)

        if source is not None:
            children.append(source)

        if cred is not None:
            children.append(cred)

        if meta is not None:
            children.append(meta)

        return cls('SyncHdr', None, children=children)

    @property
    def session_id(self):
        [session_id] = self.find('SessionID')
        return session_id.value

    @property
    def msg_id(self):
        [msg_id] = self.find('MsgID')
        return msg_id.value

    @property
    def target(self):
        [target] = self.find('Target')
        return target

    @property
    def source(self):
        [source] = self.find('Source')
        return source


class CmdID(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('CmdID', unicode(value))


class Item(SyncMLElement):

    allowed_children = [Target, Source, Meta, Data]

    @classmethod
    def create(cls, target, source, anchor):
        return cls('Item', None, children=[
            Target.create(target),
            Source.create(source),
            Meta.create(children=[anchor])])


class Alert(SyncMLElement):

    allowed_children = [CmdID, Data, Item]

    @classmethod
    def create(cls, cmd_id, code, items=[]):
        return cls('Alert', None, children=[
            CmdID.create(cmd_id),
            Data.create(code),
        ] + items)


class MsgRef(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('MsgRef', unicode(value))


class CmdRef(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('CmdRef', unicode(value))


class Cmd(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('Cmd', unicode(value))


class Chal(SyncMLElement):

    allowed_children = [Meta]

    @classmethod
    def create(cls, nonce, auth_type='syncml:auth-md5'):
        return cls('Chal', None, children=[
            Meta.create([
                Type.create(auth_type),
                Format.create('b64'),
                NextNonce.create(nonce),
            ])
        ])


class Status(SyncMLElement):

    allowed_children = [
        CmdID,
        MsgRef,
        CmdRef,
        Cmd,
        TargetRef,
        SourceRef,
        Chal,
        Data,
    ]

    @classmethod
    def create(cls, cmd_id, msg_ref, cmd_ref, cmd,
               target_ref, source_ref, code, chal=None):
        children = [
            CmdID.create(cmd_id),
            MsgRef.create(msg_ref),
            CmdRef.create(cmd_ref),
            Cmd.create(cmd),
            TargetRef.create(target_ref),
            SourceRef.create(source_ref),
            Data.create(code),
        ]
        if chal:
            children.append(chal)
        return cls('Status', None, children=children)


class Put(SyncMLElement):

    allowed_children = [
        CmdID,
        Meta,
        Item,
    ]


class SyncBody(SyncMLElement):

    allowed_children = [Alert, Meta, Status, Put, Final]

    @classmethod
    def create(cls, alerts=[], statuses=[]):
        return cls('SyncBody', None, children=(alerts + statuses))


class SyncML(SyncMLElement):

    allowed_children = [SyncHdr, SyncBody]

    @classmethod
    def create(cls, header=None, body=None):
        return cls('SyncML', None, children=filter(None, [header, body]))

    @property
    def header(self):
        return self.find(SyncHdr)[0]

    @property
    def body(self):
        return self.find(SyncBody)[0]
