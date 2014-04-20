from txsyncml.parser import SyncMLParser
from txsyncml.tests.helpers import FixtureHelper
from txsyncml.tests.test_base import TxSyncMLTestCase
from txsyncml import constants


class SyncMLParserTestCase(TxSyncMLTestCase):

    def setUp(self):
        self.fixtures = FixtureHelper()

    def test_header_parsing(self):
        data = self.fixtures.get_fixture('client_sync_init.xml')
        doc = SyncMLParser.parse(data)
        [header] = doc.find('SyncHdr')
        [verdtd] = header.find('VerDTD')
        self.assertEqual(verdtd.value, '1.1')
        [verproto] = header.find('VerProto')
        self.assertEqual(verproto.value, 'SyncML/1.1')
        [session_id] = header.find('SessionID')
        self.assertEqual(session_id.value, '1')
        [msg_id] = header.find('MsgID')
        self.assertEqual(msg_id.value, '1')
        [target] = header.find('Target')
        [target_locuri] = target.find('LocURI')
        self.assertEqual(
            target_locuri.value,
            'http://www.syncml.org/sync-server')

    def test_devinf_parsing(self):
        data = self.fixtures.get_fixture('sony-ericsson-k800i-package1.xml')
        doc = SyncMLParser.parse(data)
        [put] = doc.body.puts
        devinf = put.get_devinf()

        self.assertEqual(devinf.ver_dtd, '1.2')
        self.assertEqual(devinf.manufacturer, 'SonyEricsson')
        self.assertEqual(devinf.model, 'K800i')
        self.assertEqual(devinf.firmware_version, 'R1ED001')
        self.assertEqual(devinf.software_version, 'R6A')
        self.assertEqual(devinf.hardware_version, 'R5A')
        self.assertEqual(devinf.device_id, 'IMEI:355704019189636')
        self.assertEqual(devinf.device_type, 'phone')
        self.assertTrue(devinf.supports_utc)
        self.assertTrue(devinf.supports_large_objects)

    def test_datastores_parsing(self):
        data = self.fixtures.get_fixture('sony-ericsson-k800i-package1.xml')
        doc = SyncMLParser.parse(data)
        [put] = doc.body.puts
        devinf = put.get_devinf()
        self.assertTrue(len(devinf.datastores), 4)
        self.assertTrue(
            ['Contacts', 'Calendar', 'Tasks', 'Notes', 'Bookmarks'],
            [ds.source_ref for ds in devinf.datastores])


class ContactDataStoreTestCase(TxSyncMLTestCase):

    def setUp(self):
        self.fixtures = FixtureHelper()

    def test_contacts_datastores_parsing(self):
        data = self.fixtures.get_fixture('sony-ericsson-k800i-package1.xml')
        doc = SyncMLParser.parse(data)
        [put] = doc.body.puts
        devinf = put.get_devinf()
        ds = devinf.get_datastore('Contacts')
        self.assertEqual(ds.source_ref, 'Contacts')
        self.assertEqual(ds.display_name, 'Contacts')
        self.assertEqual(ds.max_guid_size, '64')
        self.assertEqual(ds.rx_preferred.type, 'text/x-vcard')
        self.assertEqual(ds.rx_preferred.version, '2.1')
        self.assertEqual(
            [rx.type for rx in ds.rx], ['text/x-vcard', 'text/vcard'])
        self.assertEqual(
            [rx.version for rx in ds.rx], ['2.1', '3.0'])
        self.assertEqual(ds.tx_preferred.type, 'text/x-vcard')
        self.assertEqual(ds.tx_preferred.version, '2.1')
        self.assertEqual(
            [tx.type for tx in ds.tx], ['text/x-vcard'])
        self.assertEqual(
            [tx.version for tx in ds.tx], ['2.1'])

    def test_datastore_ds_mem(self):
        data = self.fixtures.get_fixture('sony-ericsson-k800i-package1.xml')
        doc = SyncMLParser.parse(data)
        [put] = doc.body.puts
        devinf = put.get_devinf()
        ds = devinf.get_datastore('Contacts')
        self.assertEqual(ds.ds_mem.max_id, '1000')

    def test_datastore_sync_capabilities(self):
        data = self.fixtures.get_fixture('sony-ericsson-k800i-package1.xml')
        doc = SyncMLParser.parse(data)
        [put] = doc.body.puts
        devinf = put.get_devinf()
        ds = devinf.get_datastore('Contacts')
        self.assertEqual(ds.sync_capabilities, [
            constants.SYNC_CAP_TWO_WAY,
            constants.SYNC_CAP_SLOW_SYNC,
            constants.SYNC_CAP_REFRESH_FROM_CLIENT,
            constants.SYNC_CAP_REFRESH_FROM_SERVER,
            constants.SYNC_CAP_SERVER_ALERTED_SYNC,
        ])


class VCard21ParserTestCase(TxSyncMLTestCase):

    content_type = 'text/x-vcard'
    content_type_version = '2.1'

    def setUp(self):
        self.fixtures = FixtureHelper()

    def test_capabilities_parsing(self):
        data = self.fixtures.get_fixture('sony-ericsson-k800i-package1.xml')
        doc = SyncMLParser.parse(data)
        [put] = doc.body.puts
        devinf = put.get_devinf()
        ds = devinf.get_datastore('Contacts')
        cap = ds.get_capabilities(ds.rx_preferred.type)
        self.assertEqual(cap.type, ds.rx_preferred.type)
        self.assertEqual(cap.version, ds.rx_preferred.version)
        self.assertEqual(
            [prop.prop_name for prop in cap.properties],
            ['BDAY', 'URL', 'TITLE', 'ORG', 'EMAIL', 'ADR', 'NOTE',
             'TEL', 'N', 'VERSION', 'END', 'BEGIN'])

    def get_datastore(self, ds_name,
                      fixture='sony-ericsson-k800i-package1.xml'):
        data = self.fixtures.get_fixture('sony-ericsson-k800i-package1.xml')
        doc = SyncMLParser.parse(data)
        [put] = doc.body.puts
        devinf = put.get_devinf()
        return devinf.get_datastore(ds_name)

    def test_bday_property_parsing(self):
        ds = self.get_datastore('Contacts')
        cap = ds.get_capabilities(self.content_type)
        prop = cap.get_property('BDAY')
        self.assertEqual(prop.prop_name, 'BDAY')
        self.assertEqual(prop.enums, None)
        self.assertEqual(prop.max_size, None)
        self.assertEqual(prop.max_occur, None)
        self.assertEqual(prop.no_truncate, None)
        self.assertEqual(prop.params, [])

    def test_url_property_parsing(self):
        ds = self.get_datastore('Contacts')
        cap = ds.get_capabilities(self.content_type)
        prop = cap.get_property('URL')
        self.assertEqual(prop.prop_name, 'URL')
        self.assertEqual(prop.enums, None)
        self.assertEqual(prop.max_size, '120')
        self.assertEqual(prop.max_occur, None)
        self.assertEqual(prop.no_truncate, None)
        self.assertEqual(prop.params, [])

    def test_email_property_parsing(self):
        ds = self.get_datastore('Contacts')
        cap = ds.get_capabilities(self.content_type)
        prop = cap.get_property('EMAIL')
        self.assertEqual(prop.prop_name, 'EMAIL')
        self.assertEqual(prop.enums, None)
        self.assertEqual(prop.max_size, '50')
        self.assertEqual(prop.max_occur, '3')
        self.assertEqual(prop.no_truncate, True)
        [param] = prop.params
        self.assertEqual(param.param_name, 'TYPE')
        self.assertEqual(param.enums, ['INTERNET'])

    def test_adr_property_parsing(self):
        ds = self.get_datastore('Contacts')
        cap = ds.get_capabilities(self.content_type)
        prop = cap.get_property('ADR')
        self.assertEqual(prop.prop_name, 'ADR')
        self.assertEqual(prop.enums, None)
        self.assertEqual(prop.max_size, None)
        self.assertEqual(prop.max_occur, '2')
        self.assertEqual(prop.no_truncate, None)
        [param] = prop.params
        self.assertEqual(param.param_name, 'TYPE')
        self.assertEqual(param.enums, ['WORK', 'HOME'])

    def test_tel_property_parsing(self):
        ds = self.get_datastore('Contacts')
        cap = ds.get_capabilities(self.content_type)
        prop = cap.get_property('TEL')
        self.assertEqual(prop.prop_name, 'TEL')
        self.assertEqual(prop.enums, None)
        self.assertEqual(prop.max_size, '80')
        self.assertEqual(prop.max_occur, '5')
        self.assertEqual(prop.no_truncate, True)
        [param] = prop.params
        self.assertEqual(param.param_name, 'TYPE')
        self.assertEqual(
            param.enums,
            ['CELL', 'HOME', 'FAX', 'WORK'])

    def test_version_property_parsing(self):
        ds = self.get_datastore('Contacts')
        cap = ds.get_capabilities(self.content_type)
        prop = cap.get_property('VERSION')
        self.assertEqual(prop.prop_name, 'VERSION')
        self.assertEqual(prop.enums, [self.content_type_version])
        self.assertEqual(prop.max_size, None)
        self.assertEqual(prop.max_occur, None)
        self.assertEqual(prop.no_truncate, None)
        self.assertEqual(prop.params, [])


class VCard30ParserTestCase(VCard21ParserTestCase):

    content_type = 'text/vcard'
    content_type_version = '3.0'
