import pkg_resources


class FixtureHelper(object):

    def get_fixture(self, fixture_name):
        path = pkg_resources.resource_filename('txsyncml.tests.fixtures',
                                               fixture_name)
        with open(path, 'r') as fp:
            data = fp.read()
        return data
