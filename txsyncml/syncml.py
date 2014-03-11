# -*- test-case-name: txsyncml.tests.test_syncml -*-
from twisted.python import log


class SyncMLException(Exception):
    pass


class UserState(object):

    states = [
        'PACKAGE_1',  # client init
        'PACKAGE_2',  # server init
        'PACKAGE_3',  # client modifications
        'PACKAGE_4',  # server modifications
        'PACKAGE_5',  # mapping ids
        'PACKAGE_6',  # mapping status
    ]

    def __init__(self, current_state=None):
        if current_state is not None and current_state not in self.states:
            raise SyncMLException('Invalid state: %r.' % (current_state,))
        self.current_state = current_state

    @property
    def next_state(self):
        if self.current_state is None:
            next_state = self.states[0]
        else:
            current_index = self.states.index(self.current_state)
            try:
                next_state = self.states[current_index + 1]
            except IndexError:
                next_state = self.states[0]
                log.msg('Went past last state, returning to %s.' % (
                    next_state,))

        return next_state


class SyncMLEngine(object):

    def __init__(self, user_state):
        self.user_state = user_state

    def process(self, doc):
        self.process_header(doc.get_header())
        self.process_body(doc.get_body())

    def process_header(self, header):
        print header

    def process_body(self, body):
        print body
        print body.find('Alert')
