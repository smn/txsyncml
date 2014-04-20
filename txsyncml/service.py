from twisted.application import strports
from twisted.internet import reactor
from twisted.python import usage
from twisted.web import server
from twisted.internet.task import LoopingCall

from txsyncml import resource


def do_rebuild(mod):
    from twisted.python.rebuild import rebuild
    rebuild(mod, doLog=False)

lc = LoopingCall(do_rebuild, resource)
# lc.start(1)


DEFAULT_PORT = 'tcp:8080'


class Options(usage.Options):
    """Command line args when run as a twistd plugin"""
    # TODO other args
    optParameters = [["endpoint", "e", DEFAULT_PORT,
                      "Endpoint for txsyncml server to listen on"]]


def makeService(options):
    site = server.Site(resource.TxSyncMLResource(reactor=reactor))
    return strports.service(options['endpoint'], site)
