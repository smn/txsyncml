from txsyncml.tests.test_base import TxSyncMLTestCase
from txsyncml.syncml import UserState, SyncMLException


class UserStateTestCase(TxSyncMLTestCase):

    def test_start(self):
        us = UserState()
        self.assertEqual(us.get_next_state(), 'PACKAGE_1')

    def test_middle(self):
        us = UserState(current_state='PACKAGE_2')
        self.assertEqual(us.get_next_state(), 'PACKAGE_3')

    def test_end(self):
        us = UserState(current_state='PACKAGE_6')
        self.assertEqual(us.get_next_state(), 'PACKAGE_1')

    def test_invalid_state(self):
        self.assertRaises(SyncMLException, UserState, current_state='foo')
