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
            raise SyncMLError('Child %r of type %r not allowed for %r.' % (
                child, child.__class__, self.__class__))
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

    def to_dict(self):
        return {
            'name': self.name,
            'value': self.value,
            'ns': self.ns,
            'children': [child.to_dict() for child in self.children]
        }

    def find(self, child_name):
        if not isinstance(child_name, basestring):
            child_name = child_name.__name__
        return [child for child in self.children if child.name == child_name]

    def get(self, element_name, default=None):
        elements = self.find(element_name)
        if not elements:
            return default

        [element] = elements
        return element.value

    def has(self, prop_name):
        return len(self.find(prop_name)) > 0

    @property
    def cmd_id(self):
        return self.get('CmdID')


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
    def create(cls, type_):
        return cls('Type', type_, ns='syncml:metinf')


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

    @property
    def next(self):
        return self.get('Next')

    @property
    def last(self):
        return self.get('Last')

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


class Rx(SyncMLElement):

    allowed_children = (
        CTType,
        VerCT,
    )

    @property
    def type(self):
        return self.get('CTType')

    @property
    def version(self):
        return self.get('VerCT')


class Rx_Pref(Rx):
    pass


class Tx(Rx):
    pass


class Tx_Pref(Tx):
    pass

PropName = oneof('PropName')
MaxSize = oneof('MaxSize')
ParamName = oneof('ParamName')
ValEnum = oneof('ValEnum')
MaxOccur = oneof('MaxOccur')
NoTruncate = oneof('NoTruncate')


class PropParam(SyncMLElement):

    allowed_children = (
        ParamName,
        ValEnum,
    )

    @property
    def param_name(self):
        return self.get('ParamName')

    @property
    def enums(self):
        return [enum.value for enum in self.find('ValEnum')]


MaxID = oneof('MaxID')


class DSMem(SyncMLElement):

    allowed_children = (
        MaxID,
    )

    @property
    def max_id(self):
        return self.get('MaxID')


class Property(SyncMLElement):

    allowed_children = (
        PropName,
        MaxSize,
        MaxOccur,
        NoTruncate,
        PropParam,
        ValEnum,
    )

    @property
    def prop_name(self):
        return self.get('PropName')

    @property
    def max_size(self):
        return self.get('MaxSize')

    @property
    def max_occur(self):
        return self.get('MaxOccur')

    @property
    def no_truncate(self):
        if self.has('NoTruncate'):
            return True

    @property
    def params(self):
        return self.find('PropParam')

    @property
    def enums(self):
        enums = self.find('ValEnum')
        if enums:
            return [enum.value for enum in enums]


Size = oneof('Size')


class CTCap(SyncMLElement):

    allowed_children = (
        CTType,
        VerCT,
        Property,
        Size,
        ParamName,
        ValEnum,
        PropName,
    )

    @property
    def type(self):
        return self.get('CTType')

    @property
    def version(self):
        return self.get('VerCT')

    @property
    def properties(self):
        return self.find('Property')

    def get_property(self, prop_name):
        for prop in self.properties:
            if prop.prop_name == prop_name:
                return prop


SupportLargeObjs = oneof('SupportLargeObjs')
SyncType = oneof('SyncType')
SyncCap = oneof('SyncCap', [
    SyncType
])

MaxObjSize = oneof('MaxObjSize')

FreeMem = oneof('FreeMem')
FreeID = oneof('FreeID')

Mem = oneof('Mem', [
    FreeMem,
    FreeID,
])

Final = oneof('Final')


class DataStore(SyncMLElement):

    allowed_children = [
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
    ]

    @property
    def source_ref(self):
        return self.get('SourceRef')

    @property
    def display_name(self):
        return self.get('DisplayName')

    @property
    def max_guid_size(self):
        return self.get('MaxGUIDSize')

    @property
    def rx_preferred(self):
        [rx_pref] = self.find('Rx_Pref')
        return rx_pref

    @property
    def rx(self):
        return self.find('Rx_Pref') + self.find('Rx')

    @property
    def tx_preferred(self):
        [tx_pref] = self.find('Tx_Pref')
        return tx_pref

    @property
    def tx(self):
        return self.find('Tx_Pref') + self.find('Tx')

    def get_capabilities(self, cttype):
        for cap in self.find('CTCap'):
            if cap.type == cttype:
                return cap

    @property
    def ds_mem(self):
        [ds_mem] = self.find('DSMem')
        return ds_mem

    @property
    def sync_capabilities(self):
        if not self.has('SyncCap'):
            return []

        [sync_cap] = self.find('SyncCap')
        return [sync_type.value
                for sync_type in sync_cap.find('SyncType')]


class Format(SyncMLElement):

    @classmethod
    def create(cls, format_type):
        return cls('Format', format_type, ns='syncml:metinf')


class NextNonce(SyncMLElement):

    @classmethod
    def create(cls, nonce):
        return cls(
            'NextNonce', nonce.encode('base64').strip(), ns='syncml:metinf')


class Meta(SyncMLElement):

    allowed_children = [Type, Anchor, MaxMsgSize, MaxObjSize, Mem, Format,
                        NextNonce]

    @classmethod
    def create(cls, children=[]):
        return cls('Meta', None, children=children)

    @property
    def type(self):
        return self.get('Type')

    @property
    def max_object_size(self):
        return self.get('MaxObjSize')

    @property
    def anchor(self):
        return self.get('Anchor')


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

    @property
    def ver_dtd(self):
        return self.get('VerDTD')

    @property
    def manufacturer(self):
        return self.get('Man')

    @property
    def model(self):
        return self.get('Mod')

    @property
    def firmware_version(self):
        return self.get('FwV')

    @property
    def software_version(self):
        return self.get('SwV')

    @property
    def hardware_version(self):
        return self.get('HwV')

    @property
    def device_id(self):
        return self.get('DevID')

    @property
    def device_type(self):
        return self.get('DevTyp')

    @property
    def supports_utc(self):
        return self.has('UTC')

    @property
    def supports_large_objects(self):
        return self.has('SupportLargeObjs')

    @property
    def datastores(self):
        return self.find('DataStore')

    def get_datastore(self, name):
        for ds in self.find('DataStore'):
            if ds.source_ref == name:
                return ds


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

    @property
    def cmd_id(self):
        # AFAIK always 0 for SyncHdr
        return '0'


class CmdID(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('CmdID', unicode(value))


class Item(SyncMLElement):

    allowed_children = [Target, Source, Meta, Data]

    @classmethod
    def create(cls, target=None, source=None, anchor=None):
        children = []

        if target:
            children.append(Target.create(target))
        if source:
            children.append(Source.create(source))
        if anchor:
            children.append(Meta.create(children=[anchor]))

        return cls('Item', None, children=children)

    @property
    def target(self):
        [target] = self.find('Target')
        return target

    @property
    def source(self):
        [source] = self.find('Source')
        return source

    @property
    def meta(self):
        [meta] = self.find('Meta')
        return meta


class Alert(SyncMLElement):

    allowed_children = [CmdID, Data, Item]

    @classmethod
    def create(cls, cmd_id, code, items=[]):
        return cls('Alert', None, children=[
            CmdID.create(cmd_id),
            Data.create(code),
        ] + items)

    @property
    def data(self):
        return self.get('Data')

    @property
    def item(self):
        [item] = self.find('Item')
        return item


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
    def create(cls, cmd_id, msg_ref, cmd_ref, cmd, code,
               target_ref=None, source_ref=None, chal=None):
        children = [
            CmdID.create(cmd_id),
            MsgRef.create(msg_ref),
            CmdRef.create(cmd_ref),
            Cmd.create(cmd),
            Data.create(code),
        ]
        if chal:
            children.append(chal)
        if target_ref:
            children.append(TargetRef.create(target_ref))
        if source_ref:
            children.append(SourceRef.create(source_ref))
        return cls('Status', None, children=children)


class Put(SyncMLElement):

    allowed_children = [
        CmdID,
        Meta,
        Item,
    ]

    def get_item(self):
        [item] = self.find('Item')
        return item

    def get_devinf(self):
        [meta] = self.find('Meta')
        if 'devinf' in meta.type:
            item = self.get_item()
            [source] = item.find('Source')
            [data] = item.find('Data')
            [devinf] = data.find('DevInf')
            return devinf


class Get(Put):

    @classmethod
    def create(cls, cmd_id, loc_uri):
        return cls('Get', None, children=[
            CmdID.create(cmd_id),
            Meta.create(
                [Type.create('application/vnd.syncml-devinf+xml')]),
            Item.create(target=loc_uri),
        ])


class SyncBody(SyncMLElement):

    allowed_children = [Alert, Meta, Status, Get, Put, Final]

    def __init__(self, *args, **kwargs):
        super(SyncBody, self).__init__(*args, **kwargs)
        self._cmd_id = 0

    def next_cmd_id(self):
        self._cmd_id += 1
        return self._cmd_id

    @classmethod
    def create(cls, puts=[], gets=[], alerts=[], statuses=[], final=False):
        children = (alerts + statuses + puts + gets)
        if final:
            children.append(Final())
        return cls('SyncBody', None,
                   children=children)

    @property
    def alerts(self):
        return self.find('Alert')

    @property
    def puts(self):
        return self.find('Put')

    def request_devinf(self):
        self.children.append(Get.create(self.next_cmd_id(), './devinf11'))

    def status(self, msg_ref, cmd, code, **kwargs):
        self.add_child(
            Status.create(
                cmd_id=self.next_cmd_id(), msg_ref=msg_ref, cmd_ref=cmd.cmd_id,
                cmd=cmd.name, code=code, **kwargs))


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
